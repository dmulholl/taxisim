#!/usr/bin/env python3
# ----------------------------------------------------------------------------------------
# This script plots heatmaps of pickup and dropoff locations using one week of data.
# ----------------------------------------------------------------------------------------

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pickle
import sys

def long2x(long):
    return int(10000*long + 740300)

def lat2y(lat):
    return int(-13536.84*lat + 553386.1)

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

if 'pickups' in sys.argv:
    for day in range(1, 8):
        with open(f"data/requests/2016-02-{day:02d}.pickle", 'rb') as file:
            requests = pickle.load(file)
        for request in requests:
            x = long2x(request[2][1])
            y = lat2y(request[2][0])
            ax.plot(x, y, 'g,')

if 'dropoffs' in sys.argv:
    for day in range(1, 8):
        with open(f"data/requests/2016-02-{day:02d}.pickle", 'rb') as file:
            requests = pickle.load(file)
        for request in requests:
            x = long2x(request[3][1])
            y = lat2y(request[3][0])
            ax.plot(x, y, 'C3,')

plt.tight_layout()
plt.show()
fig.savefig("map.png")
