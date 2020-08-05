import enum
import sys
import random

from . import utils
from . import manhattan
from . import params


# Taxi factory. Each taxi is randomly assigned a location at a zone center. Zone probability
# is weighted according to historical demand.
def make_taxis(num, size=4, logging=False):
    return [Taxi(i, size, manhattan.get_rand_pos(), logging) for i in range(1, num + 1)]


# Identifies a taxi's current status.
class Status(enum.Enum):
    idle = "idle"
    pickup = "pickup"
    dropoff = "dropoff"
    repositioning = "repositioning"


# Identifies the nature of a task in a taxi's task list.
class Task(enum.Enum):
    pickup = "pickup"
    dropoff = "dropoff"
    reposition = "reposition"


# Identifies a taxi's last reinforcement-learning choice.
class Choice(enum.Enum):
    explore = "explore"
    exploit = "exploit"


class QTable:

    __slots__ = ["table"]

    def __init__(self):
        self.table = {1: [-1, 0, 0], params.MAXSIZE: [0, 0, -1]}

    def __getitem__(self, state):
        if state not in self.table:
            self.table[state] = [0, 0, 0]
        return self.table[state]

    def __str__(self):
        lines = []
        for state, qvals in sorted(self.table.items()):
            rowstr = ", ".join(f"{qval:8.4f}" for qval in qvals)
            lines.append(f"{state:2d}: [{rowstr}]")
        return "\n".join(lines)


class STable:

    ___slots__ = ["table"]

    def __init__(self):
        self.table = {}

    def __getitem__(self, state):
        return self.table[state]

    def __setitem__(self, state, svals):
        self.table[state] = svals

    def __contains__(self, state):
        return state in self.table

    def __str__(self):
        lines = []
        for state, svals in sorted(self.table.items()):
            lines.append(f"{state:2d}: [{svals[0]:3d}, {svals[1]:8.4f}]")
        return "\n".join(lines)

    def items(self):
        return self.table.items()


class Taxi:

    __slots__ = (
        "id", "size", "position", "num_passengers", "total_dist",
        "weighted_dist", "tasks", "status", "p_explore", "q_table",
        "last_state", "last_action", "last_choice", "num_pending_pickups",
        "logging", "log_positions", "log_pickups", "log_dropoffs",
        "s_table"
    )

    def __init__(self, id, size, position, logging=False):
        self.id = id
        self.size = size
        self.position = position
        self.num_passengers = 0
        self.num_pending_pickups = 0
        self.total_dist = 0
        self.weighted_dist = 0
        self.tasks = []
        self.status = Status.idle
        self.p_explore = 1
        self.q_table = QTable()
        self.last_state = None
        self.last_action = None
        self.last_choice = None
        self.log_positions = []
        self.log_pickups = []
        self.log_dropoffs = []
        self.logging = logging
        self.s_table = STable()

    def __str__(self):
        val = f"T{self.id} {self.status.value} "
        val += f"T{self.num_passengers}/{self.size} pos{self.position}"
        if self.tasks:
            val += f" -> dst{self.tasks[0][0]}"
        return val

    @property
    def destination(self):
        return self.tasks[0][0] if self.tasks else None

    @property
    def destinations(self):
        return [task[0] for task in self.tasks]

    @property
    def zone(self):
        return utils.get_zone(self.position)

    @property
    def reward(self):
        if self.total_dist:
            return self.weighted_dist / self.total_dist
        return 0

    @property
    def capacity(self):
        return self.size - self.num_passengers - self.num_pending_pickups

    def tick(self, world):

        # If we're idle, maybe we should reposition.
        if self.status == Status.idle and random.random() < params.REPO_PROB:
            self.append_task(manhattan.get_rand_pos(), Task.reposition)
            self.status = Status.repositioning

        if not self.tasks:
            return

        if self.logging:
            self.log_positions.append(self.position)

        # Remember the zone we started in.
        old_zone = self.zone

        # How far are we from our destination?
        destination = self.tasks[0][0]
        distance = utils.distance(self.position, destination)

        # 1. We can reach the destination within this tick.
        if distance <= params.TICK_DIST:
            self.position = destination
            self.total_dist += distance
            self.weighted_dist += self.get_weighted_dist(distance)

            while self.tasks and self.tasks[0][0] == destination:
                _, task, pg = self.tasks.pop(0)
                if task == Task.pickup:
                    self.pickup(pg, world)
                elif task == Task.dropoff:
                    self.dropoff(pg, world)
                elif task == Task.reposition:
                    pass
                else:
                    sys.exit(f"Taxi.tick(): unhandled task: {task}")

        # 2. We can't reach the destination within this tick.
        else:
            self.total_dist += params.TICK_DIST
            self.weighted_dist += self.get_weighted_dist(params.TICK_DIST)
            self.position = utils.interpolate_position(self.position, destination, params.TICK_DIST)

        # Have we moved to a new zone? Update the world.
        new_zone = self.zone
        if new_zone != old_zone:
            world.zones[old_zone].remove(self)
            world.zones.setdefault(new_zone, []).append(self)

        # Update our status.
        if self.tasks:
            if self.tasks[0][1] == Task.dropoff:
                self.status = Status.dropoff
            elif self.tasks[0][1] == Task.pickup:
                self.status = Status.pickup
            elif self.tasks[0][1] == Task.reposition:
                self.status = Status.repositioning
        else:
            self.status = Status.idle

    def choose_action(self):
        if random.random() < self.p_explore:
            self.last_choice = Choice.explore
            if self.size == 1:
                action = random.choice((0, +1))
            elif self.size == params.MAXSIZE:
                action = random.choice((-1, 0))
            else:
                action = random.choice((-1, 0, +1))
        else:
            self.last_choice = Choice.exploit
            action = self.get_best_action(self.size)
        self.last_state = self.size
        self.last_action = action
        self.size += action

    def update_q_table(self):
        new_state = self.size
        old_state = self.last_state
        index = self.last_action + 1
        self.q_table[old_state][index] = (
            (1 - params.ALPHA) *  self.q_table[old_state][index] +
            params.ALPHA * (self.reward + params.GAMMA * max(self.q_table[new_state]))
        )

    def get_best_action(self, state):
        q_values = self.q_table[state]
        max_value = max(q_values)
        indices = [i for i in range(3) if q_values[i] == max_value]
        return random.choice(indices) - 1

    def update_s_table(self):
        if self.size in self.s_table:
            n = self.s_table[self.size][0] + 1
            old_sval = self.s_table[self.size][1]
        else:
            n = 1
            old_sval = 0
        self.s_table[self.size] = (n, old_sval + (self.reward - old_sval) / n)

    def get_weighted_dist(self, dist):
        weight = self.num_passengers / self.size
        return dist * self.num_passengers * weight

    def pickup(self, pg, world):
        pg.pickup_time = world.time
        self.num_passengers += pg.size
        self.num_pending_pickups -= pg.size
        self.append_task(pg.dst_pos, Task.dropoff, pg)
        world.pickup_list.remove(pg)
        if self.logging:
            self.log_pickups.append(self.position)

    def dropoff(self, pg, world):
        pg.dropoff_time = world.time
        self.num_passengers -= pg.size
        world.update_passenger_metrics(pg)
        if self.logging:
            self.log_dropoffs.append(self.position)

    def reset_metrics(self):
        self.total_dist = 0
        self.weighted_dist = 0

    def append_task(self, pos, task, pg=None):
        self.tasks.append((pos, task, pg))

    def prepend_task(self, pos, task, pg=None):
        self.tasks.insert(0, (pos, task, pg))

    def add_pickup_task(self, pg):
        if self.status == Status.repositioning:
            self.tasks.pop(0)
        self.status = Status.pickup
        self.prepend_task(pg.src_pos, Task.pickup, pg)
        self.num_pending_pickups += pg.size
