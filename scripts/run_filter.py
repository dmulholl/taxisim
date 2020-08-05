#! /usr/bin/env python3
# ----------------------------------------------------------------------------------------
# This script filters the raw New York taxi data, producing a pickled list of request
# tuples for each day. Each request tuple has the form: (time, size, source, destination).
# ----------------------------------------------------------------------------------------

import datetime as dt
import pickle
import sys
import itertools
import os

# -------- Settings -------- #
input_file = "data/yellow_tripdata_2016-02.csv"
output_dir = "requests"
# -------------------------- #

sys.path.append('.')
import taxisim

mean_speed = 0
requests = {}
num_requests = 0
num_big_requests = 0
max_request_size = 0
sizes = {}
zones = {}

with open(input_file) as csvfile:
    headers = csvfile.readline()
    for line in csvfile:
        elements = line.split(',')
        if len(elements) != 19:
            continue

        try:
            pu_time = dt.datetime.fromisoformat(elements[1])
            do_time = dt.datetime.fromisoformat(elements[2])
            size = int(elements[3])
            pu_long = float(elements[5])
            pu_lat = float(elements[6])
            do_long = float(elements[9])
            do_lat = float(elements[10])
        except Exception as e:
            print(e)
            continue

        if pu_time.year != 2016:
            continue
        if pu_time.month != 2:
            continue
        if pu_time.hour < 8 or pu_time.hour >= 12:
            continue

        duration = (do_time - pu_time).total_seconds()
        if duration < 60 or duration > 3600:
            continue

        src_pos = (pu_lat, pu_long)
        dst_pos = (do_lat, do_long)
        if not taxisim.in_manhattan(src_pos):
            continue
        if not taxisim.in_manhattan(dst_pos):
            continue

        if size < 1 or size > 8:
            continue
        if size > 4:
            num_big_requests += 1
        if size > max_request_size:
            max_request_size = size

        num_requests += 1
        distance = taxisim.distance(src_pos, dst_pos)
        speed = distance / duration
        mean_speed += (speed - mean_speed) / num_requests
        sizes[size] = sizes.get(size, 0) + 1
        zone = taxisim.utils.get_zone(src_pos)
        zones[zone] = zones.get(zone, 0) + 1

        requests.setdefault(pu_time.day, []).append(
            (pu_time, size, src_pos, dst_pos)
        )

for day, reqlist in requests.items():
    reqlist.sort(key=lambda req: req[0])

print("\nMetadata\n--------")
print(f"Total requests: {num_requests}")
print(f"Big requests (>4): {num_big_requests}")
print(f"Percent big: {100*num_big_requests/num_requests:.2f}%")
print(f"Max request size: {max_request_size}")
print(f"Mean speed: {mean_speed}")

print()
print("Request Count By Size\n---------------------")
for size, count in sorted(sizes.items()):
    print(f"Size {size:2d}: {count} ({100*count/num_requests:.4f}%)")

print()
print("Request Count By Day\n--------------------")
for day in sorted(requests.keys()):
    print(f"Day {day:2d}: {len(requests[day])} requests")

if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

for day, reqlist in requests.items():
    with open(output_dir + f"/2016-02-{day:02d}.pickle", 'wb') as picklefile:
        pickle.dump(reqlist, picklefile)

zones_total = 0
for zone in list(zones.keys()):
    if zones[zone] < 100:
        del zones[zone]
    else:
        zones_total += zones[zone]

locations, counts, weights = [], [], []
print()
print(f"Request Count By Zone\n---------------------")
for zone, count in zones.items():
    print(f"{zone}: {count}")
    locations.append(taxisim.utils.get_zone_center(zone))
    counts.append(count)
    weights.append(count/zones_total)

cum_weights = list(itertools.accumulate(weights))
with open(output_dir + "/locations.py", 'w') as locfile:
    locfile.write(f"locations = {str(locations)}\n")
    locfile.write(f"counts = {repr(counts)}\n")
    locfile.write(f"weights = {repr(weights)}\n")
    locfile.write(f"cum_weights = {repr(cum_weights)}\n")
