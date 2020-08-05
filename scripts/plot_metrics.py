#! /usr/bin/env python3
# ----------------------------------------------------------------------------------------
# This script plots performance metrics.
# ----------------------------------------------------------------------------------------

import matplotlib.pyplot as plt
import pickle
import sys

# 3,600 taxis, size 4,  ridesharing enabled.
with open("data/metrics-3600-rs.pickle", 'rb') as file:
    metrics_rs = pickle.load(file)

# 5,500 taxis, size 4, ridesharing disabled.
with open("data/metrics-5500-nrs.pickle", 'rb') as file:
    metrics_nrs = pickle.load(file)

# 3,600 taxis, trained size distribution, ridesharing enabled.
with open("data/metrics-3600-trained.pickle", 'rb') as file:
    metrics_trained = pickle.load(file)

days = range(1, 30)

# Timeout percentage.
timeouts_rs = [metrics_rs[day]['timeouts'] for day in days]
timeouts_nrs = [metrics_nrs[day]['timeouts'] for day in days]
timeouts_trained = [metrics_trained[day]['timeouts'] for day in days]

# Mean wait time.
mwt_rs = [metrics_rs[day]['wait_time'] for day in days]
mwt_nrs = [metrics_nrs[day]['wait_time'] for day in days]
mwt_trained = [metrics_trained[day]['wait_time'] for day in days]

# Mean journey time.
mjt_rs = [metrics_rs[day]['journey_time'] for day in days]
mjt_nrs = [metrics_nrs[day]['journey_time'] for day in days]
mjt_trained = [metrics_trained[day]['journey_time'] for day in days]

# Service thresholds.
mwt_threshold = [5 for day in days]
timeouts_threshold = [0.5 for day in days]

# ----------------------------------------------------------------------------------------
# Timeouts for the trained distribution.
# ----------------------------------------------------------------------------------------

if 'trained-timeouts' in sys.argv:
    fig, ax = plt.subplots()
    ax.plot(days, timeouts_rs, 'o-')
    ax.plot(days, timeouts_trained, 'o-', color='C3')
    ax.set_xlabel("Day", fontweight='bold', labelpad=10)
    ax.set_ylabel("Timeout Percentage", fontweight='bold', labelpad=10)
    ax.legend(labels=('uniform taxi size', 'trained distribution'), loc='upper left')
    plt.tight_layout()
    plt.show()
    fig.savefig("trained-timeouts.eps")

# ----------------------------------------------------------------------------------------
# Mean wait time for the trained distribution.
# ----------------------------------------------------------------------------------------

if 'trained-mwt' in sys.argv:
    fig, ax = plt.subplots()
    ax.plot(days, mwt_rs, 'o-')
    ax.plot(days, mwt_trained, 'o-', color='C3')
    ax.set_ylim(top=5.5, bottom=0)
    ax.set_xlabel("Day", fontweight='bold', labelpad=10)
    ax.set_ylabel("Mean Wait Time (minutes)", fontweight='bold', labelpad=10)
    ax.legend(labels=('uniform taxi size', 'trained distribution'), loc='upper left')
    plt.tight_layout()
    plt.show()
    fig.savefig("trained-mwt.eps")

# ----------------------------------------------------------------------------------------
# Mean journey time for the trained distribution.
# ----------------------------------------------------------------------------------------

if 'trained-mjt' in sys.argv:
    fig, ax = plt.subplots()
    ax.plot(days, mjt_rs, 'o-')
    ax.plot(days, mjt_trained, 'o-', color='C3')
    ax.set_ylim(top=13.5, bottom=11)
    ax.set_xlabel("Day", fontweight='bold', labelpad=10)
    ax.set_ylabel("Mean Journey Time (minutes)", fontweight='bold', labelpad=10)
    ax.legend(labels=('uniform taxi size', 'trained distribution'), loc='upper left')
    plt.tight_layout()
    plt.show()
    fig.savefig("trained-mjt.eps")

# ----------------------------------------------------------------------------------------
# Mean wait time.
# ----------------------------------------------------------------------------------------

if 'mwt' in sys.argv:
    fig, ax = plt.subplots()
    ax.plot(days, mwt_nrs, 'o-', color='C0', zorder=10)
    ax.plot(days, mwt_rs, 'o-', color='C3', zorder=20)
    ax.plot(days, mwt_threshold, '--', color='black')
    ax.set_ylim(top=6, bottom=0)
    ax.set_xlabel("Day", fontweight='bold', labelpad=10)
    ax.set_ylabel("Mean Wait Time (minutes)", fontweight='bold', labelpad=10)
    ax.legend(
        labels=('5500 taxis, no ridesharing', '3600 taxis, ridesharing', 'service threshold'),
        loc='lower center',
        bbox_to_anchor=(0.5, 0.105)
    )
    plt.tight_layout()
    plt.show()
    fig.savefig("mwt.eps")

# ----------------------------------------------------------------------------------------
# Timeouts.
# ----------------------------------------------------------------------------------------

if 'timeouts' in sys.argv:
    fig, ax = plt.subplots()
    ax.plot(days, timeouts_nrs, 'o-', color='C0')
    ax.plot(days, timeouts_rs, 'o-', color='C3')
    ax.plot(days, timeouts_threshold, '--', color='black')
    ax.set_ylim(top=0.55, bottom=0)
    ax.set_xlabel("Day", fontweight='bold', labelpad=10)
    ax.set_ylabel("Timeout Percentage", fontweight='bold', labelpad=10)
    ax.legend(
        labels=('5500 taxis, no ridesharing', '3600 taxis, ridesharing', 'service threshold'),
        loc='upper left',
        bbox_to_anchor=(0.035, 0.85)
    )
    plt.tight_layout()
    plt.show()
    fig.savefig("timeouts.eps")
