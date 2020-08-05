#! /usr/bin/env pypy3
# ----------------------------------------------------------------------------------------
# This script runs the simulation for a single day. No training takes place.
# ----------------------------------------------------------------------------------------

import datetime as dt
import pickle
import sys

# -------- Settings -------- #
day = 1
num_taxis = 5250
enable_sharing = False
save_taxipaths = False
# -------------------------- #

sys.path.append('.')
import taxisim

if day < 1 or day > 29:
    sys.exit("Error: check your calender.")

with open(f"data/requests/2016-02-{day:02d}.pickle", 'rb') as file:
    requests = pickle.load(file)

taxis = taxisim.make_taxis(num_taxis, logging=save_taxipaths)

world = taxisim.World(ridesharing=enable_sharing, log_ticks=True)
world.add_taxis(taxis)
world.time = dt.datetime(2016, 2, day, 8)
world.add_requests(requests)
world.run()

if save_taxipaths:
    paths = {}
    for taxi in taxis:
        paths[taxi.id] = {
            "positions": taxi.log_positions,
            "pickups": taxi.log_pickups,
            "dropoffs": taxi.log_dropoffs
        }
    with open("paths.pickle", 'wb') as file:
        pickle.dump(paths, file)
