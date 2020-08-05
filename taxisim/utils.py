import math
import random
import taxisim

from math import cos, sin, atan2, asin, sqrt


# Average earth radius in meters.
EARTH_RADIUS = 6371009


# Calculate the great-circle distance in meters between two points on the earth's surface using
# the haversine formula. This formula remains well-conditioned for small distances with an error
# of up to approx 0.5%. Positions should be specified as (lat, long) tuples with angles in degrees.
# Ref: http://www.movable-type.co.uk/scripts/latlong.html
def distance(pos1, pos2):
    phi_1 = math.radians(pos1[0])       # latitude 1 in radians
    lambda_1 = math.radians(pos1[1])    # longitude 1 in radians
    phi_2 = math.radians(pos2[0])       # latitude 2 in radians
    lambda_2 = math.radians(pos2[1])    # longitude 2 in radians

    delta_phi = phi_2 - phi_1
    delta_lambda = lambda_2 - lambda_1

    a = (sin(delta_phi/2) ** 2) + cos(phi_1) * cos(phi_2) * (sin(delta_lambda/2) ** 2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return EARTH_RADIUS * c


# Total distance in meters of the path connecting a sequence of positions.
# Positions should be specified as (lat, long) tuples with angles in degrees.
def total_distance(*positions):
    i, total = 0, 0
    while i <= len(positions) - 2:
        total += distance(positions[i], positions[i+1])
        i += 1
    return total


# Calculate the position of an intermediate point along the great circle from pos1 to pos2 located
# dist meters from pos1. Positions are (lat, long) tuples with angles in degrees.
# Ref: http://www.movable-type.co.uk/scripts/latlong.html
def interpolate_position(pos1, pos2, dist):
    phi_1 = math.radians(pos1[0])       # latitude 1 in radians
    lambda_1 = math.radians(pos1[1])    # longitude 1 in radians
    phi_2 = math.radians(pos2[0])       # latitude 2 in radians
    lambda_2 = math.radians(pos2[1])    # longitude 2 in radians

    # Determine the initial bearing pos1 -> pos2, theta.
    lambda_d = lambda_2 - lambda_1
    y = sin(lambda_d) * cos(phi_2)
    x = cos(phi_1) * sin(phi_2) - sin(phi_1) * cos(phi_2) * cos(lambda_d)
    theta = atan2(y, x)

    # Determine destination given distance and bearing.
    delta = dist / EARTH_RADIUS         # angular distance to travel
    phi_i = asin(
        sin(phi_1) * cos(delta) + cos(phi_1) * sin(delta) * cos(theta)
    )
    lambda_i = lambda_1 + atan2(
        sin(theta) * sin(delta) * cos(phi_1),
        cos(delta) - sin(phi_1) * sin(phi_2)
    )

    # Back to degrees and normalize.
    lat = math.degrees(phi_i)
    long = (math.degrees(lambda_i) + 540) % 360 - 180
    return (lat, long)


# Basic logging. Will log to a file if taxisim.logfile is set.
def log(msg, time=None):
    output = f"[{time}]  >>  {msg}" if time else msg
    print(output)
    if taxisim.logfile:
        taxisim.logfile.write(output)
        taxisim.logfile.write('\n')


# Returns the zone ID for the specified (lat, long) position tuple. A zone is identified by the
# coordinates of its lower-left corner in hundreths of a degree converted into integers to avoid
# floating-point weirdness. Each zone is one-hundreth of a degree of latitude tall (approx.
# 1112m) and one-hundreth of a degree of longitude wide (approx. 843m).
# Example: pos(40.713, -74.005) -> pos(40.71, -74.01) -> zone(4017, -7401).
def get_zone(pos):
    lat, long = pos
    return (math.floor(lat*100), math.floor(long*100))


# Returns a list containing the position's own zone and all 8 immediately-neighbouring zones.
# The zone containing the position is the first element in the list.
def get_neighbouring_zones(pos):
    zone = get_zone(pos)
    neighbours = [zone]
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            if not (i == 0 and j == 0):
                neighbours.append((zone[0] + i, zone[1] + j))
    return neighbours


# Returns the (lat, long) coordinates of the zone's center.
def get_zone_center(zone):
    lat = zone[0] / 100 + 0.005
    long = zone[1] / 100 + 0.005
    return (lat, long)


# If k is greater than the population size, returns the population. Otherwise
# returns a k-length list of unique elements chosen randomly without replacement.
def sample(population, k):
    if k >= len(population):
        return population
    else:
        return random.sample(population, k)


# Returns true if a (lat, long) position is inside a bounding box identified by the (lat, long)
# positions of its (bottom_left, top_right) corners.
def in_box(pos, box):
    lat, long = pos
    bl_lat, bl_long = box[0]
    tr_lat, tr_long = box[1]
    if lat >= bl_lat and lat <= tr_lat:
        if long >= bl_long and long <= tr_long:
            return True
    return False
