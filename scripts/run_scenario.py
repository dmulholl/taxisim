#! /usr/bin/env pypy3
# ----------------------------------------------------------------------------------------
# This script runs the simulation for a simple scenario.
# ----------------------------------------------------------------------------------------

import datetime as dt
import sys

sys.path.append('.')
import taxisim

world = taxisim.World(ridesharing=True, log_ticks=True)
world.time = dt.datetime(2016, 2, 1, 8)

world.add_taxi(taxisim.Taxi(1, 4, (40.7647, -73.9732)))

world.add_requests([
    (dt.datetime(2016, 2, 1,  8,  1), 1, (40.7683, -73.9812), (40.7818, -73.9714)),
    (dt.datetime(2016, 2, 1,  8,  2), 1, (40.7720, -73.9787), (40.8000, -73.9579)),
])

world.run()
