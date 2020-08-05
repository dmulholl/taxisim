#!/usr/bin/env python3
# ----------------------------------------------------------------------------------------
# This script plots a map of Manhattan with a grid showing the model's dispatch zones.
# ----------------------------------------------------------------------------------------

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

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

ax.grid(which='both')
ax.grid(which='major', color='black')

plt.tight_layout()
plt.show()
fig.savefig("map.png")
