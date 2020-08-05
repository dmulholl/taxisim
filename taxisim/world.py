import datetime as dt
import random
import time
import itertools

from . import utils
from . import manhattan
from . import params
from .taxi import Status


class World:

    def __init__(self, ridesharing=False, log_ticks=False):

        # Public.
        self.time = None                # Current simulation datetime.
        self.ridesharing = ridesharing  # If true, ridesharing is enabled.
        self.log_ticks = log_ticks      # If true, log status every tick.

        # Private.
        self.request_queue = []         # Incoming request tuples.
        self.taxis = []                 # Master list of all taxis.
        self.zones = {}                 # Taxi lists indexed by zone.
        self.dispatch_queue = []        # Passenger groups waiting for dispatch.
        self.pickup_list = []           # Passenger groups waiting for pickup.

        # Read-only metrics.
        self.num_requests = 0           # Total requests processed so far.
        self.num_dropoffs = 0           # Total successful dropoffs.
        self.num_timeouts = 0           # Total timeouts while awaiting dispatch.
        self.mean_dispatch_time = 0     # Mean time in minutes spent awaiting dispatch.
        self.mean_pickup_time = 0       # Mean time in minutes spent awaiting pickup.
        self.mean_journey_time = 0      # Mean time in minutes spent in taxi.

        # Time delta conversions.
        self.timeout = dt.timedelta(minutes=params.TIMEOUT)
        self.tick_time = dt.timedelta(seconds=params.TICK_TIME)
        self.split_time = dt.timedelta(minutes=params.SPLIT_TIME)

    def __str__(self):
        out = f"R: {self.num_requests:6d}    "
        out += f"DQ: {len(self.dispatch_queue):4d}    "
        out += f"PL: {len(self.pickup_list):4d}    "
        out += f"DO: {self.num_dropoffs:6d}    "
        out += f"TO: {self.num_timeouts:4d} ({self.timeout_percent:.2f}%)    "
        out += f"MD: {self.mean_dispatch_time:.2f}    "
        out += f"MP: {self.mean_pickup_time:.2f}    "
        out += f"MW: {self.mean_wait_time:.2f}    "
        out += f"MJ: {self.mean_journey_time:5.2f}"
        return out

    # Percentage of requests that have timed-out.
    @property
    def timeout_percent(self):
        if self.num_requests > 0:
            return 100 * self.num_timeouts / self.num_requests
        else:
            return 0

    # Mean passenger wait-time (i.e. total time spent waiting for a taxi to arrive).
    @property
    def mean_wait_time(self):
        return self.mean_dispatch_time + self.mean_pickup_time

    # Add a single Taxi instance.
    def add_taxi(self, taxi):
        self.zones.setdefault(taxi.zone, []).append(taxi)
        self.taxis.append(taxi)

    # Add a list of Taxi instances.
    def add_taxis(self, taxis):
        for taxi in taxis:
            self.add_taxi(taxi)

    # Add a list of request tuples to the request queue.
    # Each tuple should have the form: (time, size, source, destination).
    def add_requests(self, requests):
        self.request_queue.extend(requests)

    # Add a single request tuple to the request queue.
    def add_request(self, request):
        self.request_queue.append(request)

    # Run the simulation until all requests in the queue have been processed.
    def run(self):
        run_start_time = time.time()
        mean_tick_time, num_ticks = 0, 0
        while True:
            tick_start_time = time.time()
            self.tick()
            if self.log_ticks:
                num_ticks += 1
                tick_time = time.time() - tick_start_time
                mean_tick_time += (tick_time - mean_tick_time) / num_ticks
                run_time = (time.time() - run_start_time) / 60
                msg = f"ENDTICK  "
                msg += f"[{tick_time:5.2f}s|{mean_tick_time:5.2f}s|{run_time:5.2f}m]"
                msg += f"  >>  {self}"
                utils.log(msg, self.time)
            if not self.request_queue:
                if self.num_requests == self.num_dropoffs + self.num_timeouts:
                    break

    # Advance the simulation by one tick.
    def tick(self):
        self.time += self.tick_time
        for taxi in self.taxis:
            taxi.tick(self)
        self.load_requests()
        self.dispatch_taxis()

    # Process pending passenger requests for the current tick.
    def load_requests(self):
        while self.request_queue and self.request_queue[0][0] <= self.time:
            time, size, src_pos, dst_pos = self.request_queue.pop(0)
            pg = PassengerGroup(self.time, size, src_pos, dst_pos)
            self.dispatch_queue.append(pg)
            self.num_requests += 1

    # Try to find a taxi for each passenger group in the dispatch queue.
    def dispatch_taxis(self):
        taxi, last_pg = None, None
        for pg in self.dispatch_queue.copy():
            waiting_time = self.time - pg.request_time
            if waiting_time >= self.timeout:
                self.dispatch_queue.remove(pg)
                self.update_passenger_metrics(pg, timeout=True)
                continue
            if taxi and last_pg.group_id == pg.group_id and taxi.capacity >= pg.size:
                pass
            else:
                taxi = self.get_closest_available_taxi(pg)
            if taxi:
                taxi.add_pickup_task(pg)
                self.dispatch_queue.remove(pg)
                self.pickup_list.append(pg)
                pg.dispatch_time = self.time
                last_pg = pg
            elif pg.size >= params.SPLIT_SIZE and waiting_time >= self.split_time:
                new_pg = pg.split(int(pg.size / 2))
                index = self.dispatch_queue.index(pg)
                self.dispatch_queue.insert(index, new_pg)
                self.num_requests += 1

    # Find the closest available taxi that can service the passenger group's request.
    # The group's zone and the 8 immediate neighbouring zones are checked for taxis.
    def get_closest_available_taxi(self, pg):
        zone_candidates = []
        for zone in utils.get_neighbouring_zones(pg.src_pos):
            if self.ridesharing:
                taxi, distance, instant = self.get_zone_candidate_rs(zone, pg)
            else:
                taxi, distance, instant = self.get_zone_candidate_no_rs(zone, pg)
            if instant:
                return taxi
            elif taxi:
                zone_candidates.append((distance, taxi))
        if zone_candidates:
            zone_candidates.sort(key=lambda e: e[0])
            return zone_candidates[0][1]
        else:
            return None

    # Find the closest available taxi in the specified zone that can service the
    # passenger's request. No ridesharing.
    def get_zone_candidate_no_rs(self, zone, pg):
        available_taxis = []
        for taxi in self.zones.get(zone, []):
            if taxi.capacity >= pg.size:
                if taxi.status in (Status.idle, Status.repositioning):
                    available_taxis.append(taxi)
        candidates = []
        for taxi in available_taxis:
            distance = utils.distance(pg.src_pos, taxi.position)
            if distance < params.INSTANT_DISPATCH_RANGE:
                return taxi, distance, True
            candidates.append((distance, taxi))
        if candidates:
            candidates.sort(key=lambda e: e[0])
            return candidates[0][1], candidates[0][0], False
        else:
            return None, None, False

    # Find the closest available taxi in the specified zone that can service the
    # passenger's request. Ridesharing enabled.
    def get_zone_candidate_rs(self, zone, pg):
        available_taxis = []
        for taxi in self.zones.get(zone, []):
            if taxi.capacity >= pg.size:
                if taxi.status in (Status.dropoff, Status.idle, Status.repositioning):
                    available_taxis.append(taxi)
        candidates = []
        for taxi in available_taxis:
            dist_to_taxi = utils.distance(pg.src_pos, taxi.position)
            if taxi.status == Status.dropoff:
                d1 = utils.distance(taxi.position, taxi.destination)
                d2 = dist_to_taxi + utils.distance(pg.src_pos, taxi.destination)
                if d2 <= d1 * params.RIDESHARE_MULTIPLIER:
                    rs_dist = utils.total_distance(
                        pg.src_pos, *taxi.destinations, pg.dst_pos
                    )
                    if rs_dist <= pg.rs_distance_limit:
                        candidates.append((dist_to_taxi, taxi))
            else:
                candidates.append((dist_to_taxi, taxi))
            if candidates and candidates[-1][0] < params.INSTANT_DISPATCH_RANGE:
                return candidates[-1][1], candidates[-1][0], True
        if candidates:
            candidates.sort(key=lambda e: e[0])
            return candidates[0][1], candidates[0][0], False
        else:
            return None, None, False

    # This function is called whenever a passenger group is dropped-off or the request times-out.
    def update_passenger_metrics(self, pg, timeout=False):
        if timeout:
            self.num_timeouts += 1
            n = self.num_timeouts + self.num_dropoffs
            self.mean_dispatch_time += (params.TIMEOUT - self.mean_dispatch_time) / n
        else:
            self.num_dropoffs += 1
            n = self.num_timeouts + self.num_dropoffs
            dispatch_time = (pg.dispatch_time - pg.request_time).total_seconds() / 60
            pickup_time = (pg.pickup_time - pg.dispatch_time).total_seconds() / 60
            journey_time = (pg.dropoff_time - pg.pickup_time).total_seconds() / 60
            self.mean_dispatch_time += (dispatch_time - self.mean_dispatch_time) / n
            self.mean_pickup_time += (pickup_time - self.mean_pickup_time) / self.num_dropoffs
            self.mean_journey_time += (journey_time - self.mean_journey_time) / self.num_dropoffs

    # Reset each taxi's metrics and randomly assign it a new location.
    def reset_taxis(self):
        self.zones = {}
        for taxi in self.taxis:
            taxi.reset_metrics()
            taxi.position = manhattan.get_rand_pos()
            self.zones.setdefault(taxi.zone, []).append(taxi)

    # Reset world metrics.
    def reset_metrics(self):
        self.num_requests = 0
        self.num_dropoffs = 0
        self.num_timeouts = 0
        self.mean_dispatch_time = 0
        self.mean_pickup_time = 0
        self.mean_journey_time = 0


# A PassengerGroup instance represents a group of passengers travelling together as a unit.
class PassengerGroup:

    __slots__ = (
        "request_time", "size", "src_pos", "dst_pos", "rs_distance_limit",
        "dispatch_time", "pickup_time", "dropoff_time", "group_id"
    )

    id_iter = itertools.count(1)

    def __init__(self, request_time, size, src_pos, dst_pos, group_id=None):
        self.request_time = request_time
        self.size = size
        self.src_pos = src_pos
        self.dst_pos = dst_pos
        self.rs_distance_limit = utils.distance(src_pos, dst_pos) * params.RIDESHARE_MULTIPLIER
        self.dispatch_time = None
        self.pickup_time = None
        self.dropoff_time = None
        self.group_id = group_id or next(self.id_iter)

    def split(self, split_size):
        new_pg = PassengerGroup(
            self.request_time, split_size, self.src_pos, self.dst_pos, self.group_id
        )
        new_pg.dispatch_time = self.dispatch_time
        new_pg.pickup_time = self.pickup_time
        new_pg.dropoff_time = self.dropoff_time
        new_pg.rs_distance_limit = self.rs_distance_limit
        self.size -= split_size
        return new_pg
