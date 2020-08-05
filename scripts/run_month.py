#! /usr/bin/env pypy3
# ----------------------------------------------------------------------------------------
# This script runs the simulation for one full month, or for any specified interval of
# days within the month. No training takes place.
# ----------------------------------------------------------------------------------------

import datetime as dt
import sys
import pickle
import time

# -------- Settings -------- #
start_day = 1
end_day = 29
num_taxis = 3600
enable_sharing = True
save_metrics = False
# -------------------------- #

sys.path.append('.')
import taxisim

if start_day < 1 or end_day > 29:
    sys.exit("Error: check your calender.")

max_timeout = 0
max_wait = 0
start_time = time.time()
metrics = dict()

requests = {}
for day in range(start_day, end_day + 1):
    filename = f"data/requests/2016-02-{day:02d}.pickle"
    with open(filename, 'rb') as file:
        requests[day] = pickle.load(file)

if num_taxis == 'trained':
    with open("data/q-training-log-2000.pickle", 'rb') as file:
        logfile = pickle.load(file)
    taxis = []
    for size, count in logfile['runs'][2000]['sizes'].items():
        taxis.extend(taxisim.make_taxis(count, size=size))
else:
    taxis = taxisim.make_taxis(num_taxis)

world = taxisim.World(ridesharing=enable_sharing)
world.add_taxis(taxis)

print(f"Running month, {num_taxis} taxis, ridesharing = {enable_sharing}\n")

for day in range(start_day, end_day + 1):
    day_start = time.time()
    world.time = dt.datetime(2016, 2, day, 8)
    world.add_requests(requests[day])
    world.reset_taxis()
    world.reset_metrics()
    world.run()
    day_time = (time.time() - day_start) / 60
    stats = f"TO: {world.timeout_percent:.4f}%    MW: {world.mean_wait_time:.2f}"
    print(f"[{day_time:.2f}m]    Day: {day:2d}    {stats}")
    if world.timeout_percent > max_timeout:
        max_timeout = world.timeout_percent
    if world.mean_wait_time > max_wait:
        max_wait = world.mean_wait_time
    metrics[day] = {
        'timeouts': world.timeout_percent,
        'wait_time': world.mean_wait_time,
        'journey_time': world.mean_journey_time,
    }

sim_time = (time.time() - start_time) / 60

print(f"\nMax timeout: {max_timeout:.2f}%")
print(f"Max wait:    {max_wait:.2f}m")
print(f"Sim time:    {sim_time:.2f}m")

if save_metrics:
    with open("metrics.pickle", 'wb') as file:
        pickle.dump(metrics, file)
