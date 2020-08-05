#! /usr/bin/env python3
# ----------------------------------------------------------------------------------------
# This script plots a bar chart showing total daily trip numbers for February 2016
# (08:00 to 12:00).
# ----------------------------------------------------------------------------------------

import matplotlib.pyplot as plt

days = range(1, 30)
labels = [str(day) for day in days]

requests = [
    60540, 67177, 70058, 70098, 66502, 53920, 44211, 64821, 68903, 71095, 76731,
    73807, 58257, 52000, 58077, 69393, 68484, 70557, 68709, 52110, 46004, 62088,
    73405, 78445, 68933, 72920, 57357, 44968, 64270,
]

fig, ax = plt.subplots(figsize=(10,5))
ax.bar(days, requests, width=0.9, tick_label=labels)
ax.set_xlabel("Day (February 2016)", fontweight='bold', labelpad=10)
ax.set_ylabel("Number of Trips", fontweight='bold', labelpad=10)

plt.tight_layout()
plt.show()
fig.savefig("image.eps")
