#!/usr/bin/env python3
# ----------------------------------------------------------------------------------------
# This script plots individual taxi paths.
# ----------------------------------------------------------------------------------------

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pickle
import sys
import os

logfile = "data/paths-rs.pickle"
out_dir = "paths-rs"
num_taxis = 25

if not os.path.isdir(out_dir):
    os.makedirs(out_dir)

with open(logfile, 'rb') as file:
    taxilogs = pickle.load(file)

def long2x(long):
    return int(10000 * long + 740300)

def lat2y(lat):
    return int(-13536.84 * lat + 553386.1)

for i in range(1, num_taxis + 1):
    taxilog = taxilogs[i]

    positions = list(dict.fromkeys(taxilog['positions']))
    pickups = list(dict.fromkeys(taxilog['pickups']))
    dropoffs = list(dict.fromkeys(taxilog['dropoffs']))

    last_dropoff = dropoffs[-1]

    if last_dropoff in positions:
        index = positions.index(last_dropoff)
        positions = positions[:index + 1]

    xvals = [long2x(long) for lat, long in positions]
    yvals = [lat2y(lat) for lat, long in positions]

    img = mpimg.imread('data/map.png')
    fig, ax = plt.subplots(figsize=(6, 8))
    ax.imshow(img)

    yticks_minor = [int(f) for f in range(135, 2500, 135)]
    ax.set_yticks(yticks_minor, minor=True)
    ax.set_yticks((405, 1080, 1755, 2430), minor=False)
    ax.set_yticklabels(('40.85', '40.80', '40.75', '40.70'), minor=False)
    ax.set_ylabel('Latitude', fontweight='bold', labelpad=10)

    xticks_minor = range(100, 1300, 100)
    ax.set_xticks(xticks_minor, minor=True)
    ax.set_xticks((300, 800, 1300), minor=False)
    ax.set_xticklabels(('-74.00', '-73.95', '-73.90'), minor=False)
    ax.set_xlabel('Longitude', fontweight='bold', labelpad=15)

    ax.plot(xvals, yvals, 'k-')
    ax.plot(xvals[0], yvals[0], 'ko')

    for pos in pickups:
        x = long2x(pos[1])
        y = lat2y(pos[0])
        ax.plot(x, y, 'ko')
        ax.plot(x, y, 'go', markersize=4)

    for pos in dropoffs:
        x = long2x(pos[1])
        y = lat2y(pos[0])
        ax.plot(x, y, 'ko')
        ax.plot(x, y, 'ro', markersize=4)

    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.25)
    fig.savefig(out_dir + f"/taxi-{i:03d}.png")
    plt.close()
