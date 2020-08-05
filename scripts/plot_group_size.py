#! /usr/bin/env python3
# ----------------------------------------------------------------------------------------
# This script plots a bar chart showing passenger group size as a percentage of total
# requests.
# ----------------------------------------------------------------------------------------

import matplotlib.pyplot as plt

sizes = range(1, 8)
labels = [str(size) for size in sizes]

counts = [
    74.4747,
    11.5842,
    3.2841,
    1.5109,
    5.4258,
    3.7202,
    0.0001,
]

fig, ax = plt.subplots()
ax.bar(sizes, counts, width=0.8, tick_label=labels)
ax.set_xlabel("Passenger Group Size", fontweight='bold', labelpad=10)
ax.set_ylabel("Percentage of Total Requests (%)", fontweight='bold', labelpad=10)

plt.tight_layout()
plt.show()
fig.savefig("image.eps")
