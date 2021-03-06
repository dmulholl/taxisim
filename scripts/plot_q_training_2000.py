#! /usr/bin/env python3
# ----------------------------------------------------------------------------------------
# Q-training plots.
# ----------------------------------------------------------------------------------------

import matplotlib.pyplot as plt
import pickle
import sys

max_size = 16
num_runs = 2000

colors1 = [
    "#4E73A3", "#9E4D48", "#8FA359", "#5897AC", "#D0874C", "#97A9CD", "#6D5A8B", "#C79593",
    "#BECC9C", "#A69CBB", "#776143", "#B6935B", "#855943",
]

colors2 = [
    "#2F67AE", "#BD4C20", "#317150", "#C62D4A", "#6D38C3", "#337581", "#223ACC", "#862670",
    "#446270", "#C63F38", "#234B7B", "#6699D5", "#DA7949", "#4FA67C", "#DC577C", "#8C64C9",
    "#4AA2B2", "#5163EB", "#B0479A", "#718792", "#DE706C", "#3B6493",
]

with open(f"data/q-training-log-{num_runs}.pickle", 'rb') as file:
    log = pickle.load(file)

# ----------------------------------------------------------------------------------------
# Stacked area plot
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
    fig.savefig("areas.png")

# ----------------------------------------------------------------------------------------
# Bar chart
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
    fig.savefig("bars.eps")

# ----------------------------------------------------------------------------------------
# Timeouts
# ----------------------------------------------------------------------------------------


runs = range(1, num_runs + 1)
timeouts = [log['runs'][run_num]['timeout_percent'] for run_num in range(1, num_runs + 1)]

if 'timeouts' in sys.argv:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(runs, timeouts)
    ax.set_xlabel("Day", fontweight='bold', labelpad=10)
    ax.set_ylabel("Timeout Percentage", fontweight='bold', labelpad=10)
    plt.tight_layout()
    plt.show()
    fig.savefig("timeouts.eps")

# ----------------------------------------------------------------------------------------
# MWT
# ----------------------------------------------------------------------------------------

runs = range(1, num_runs + 1)
times = [log['runs'][run_num]['mean_wait'] for run_num in range(1, num_runs + 1)]

if 'mwt' in sys.argv:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(runs, times)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Day", fontweight='bold', labelpad=10)
    ax.set_ylabel("Mean Wait Time (minutes)", fontweight='bold', labelpad=10)
    plt.tight_layout()
    plt.show()
    fig.savefig("mwt.eps")
