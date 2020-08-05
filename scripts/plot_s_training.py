#! /usr/bin/env python3
# ----------------------------------------------------------------------------------------
# Monte Carlo sample learning plots.
# ----------------------------------------------------------------------------------------

import matplotlib.pyplot as plt
import pickle
import sys

max_size = 16
num_runs = 1000

colors1 = [
    "#4E73A3", "#9E4D48", "#8FA359", "#5897AC", "#D0874C", "#97A9CD", "#6D5A8B", "#C79593",
    "#BECC9C", "#A69CBB", "#776143", "#B6935B", "#855943",
]

colors2 = [
    "#2F67AE", "#BD4C20", "#317150", "#C62D4A", "#6D38C3", "#337581", "#223ACC", "#862670",
    "#446270", "#C63F38", "#234B7B", "#6699D5", "#DA7949", "#4FA67C", "#DC577C", "#8C64C9",
    "#4AA2B2", "#5163EB", "#B0479A", "#718792", "#DE706C", "#3B6493",
]

with open(f"data/s-training-log-1000.pickle", 'rb') as file:
    log = pickle.load(file)

# ----------------------------------------------------------------------------------------
# Stacked area plot showing the size distribution on each day of training.
# ----------------------------------------------------------------------------------------

sizedict = {size: [] for size in range(1, max_size + 1)}
for run_num in range(0, num_runs + 1):
    for size in range(1, max_size + 1):
        sizedict[size].append(log['runs'][run_num]['sizes'].get(size, 0))

x = range(0, num_runs + 1)
y = [sizedict[size] for size in range(1, max_size + 1)]
labels = [str(size) for size in range(1, max_size + 1)]

if 'area' in sys.argv:
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.stackplot(x, y, labels=labels, colors=colors1)
    ax.legend(loc='center', bbox_to_anchor=(0.5, -0.225), ncol=8)
    ax.set_xlabel("Day", fontweight='bold', labelpad=10)
    ax.set_ylabel("Number of Taxis", fontweight='bold', labelpad=10)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.15, box.width, box.height * 0.85])
    plt.show()
    fig.savefig("s-training.png")

# ----------------------------------------------------------------------------------------
# Bar chart showing the size distribution on the final day.
# ----------------------------------------------------------------------------------------

sizes = range(1, max_size + 1)
counts = [log['runs'][num_runs]['sizes'].get(size, 0) for size in sizes]
labels = [str(size) for size in sizes]

if 'bars' in sys.argv:
    fig, ax = plt.subplots()
    ax.bar(sizes, counts, width=0.95, tick_label=labels)
    ax.set_xlabel("Taxi Size", fontweight='bold', labelpad=10)
    ax.set_ylabel("Number of Taxis", fontweight='bold', labelpad=10)
    plt.tight_layout()
    plt.show()
    fig.savefig("final-dist-s.eps")
