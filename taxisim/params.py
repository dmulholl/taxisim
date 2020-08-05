# ----------------------------------------------------------------------------------------
# Direct parameters.
# ----------------------------------------------------------------------------------------

# Length in seconds of one simulation tick.
TICK_TIME = 60

# Taxi speed in m/s. (3.3571 m/s ~ 200m/min ~ 12 km/h.)
TAXI_SPEED = 3.3571

# Max time in minutes a passenger will wait for a taxi to be dispatched.
TIMEOUT = 10

# Mean time in minutes an idle taxi should wait before repositioning.
MEAN_REPO_TIME = 10

# A passenger will be willing to share a ride if the ridesharing distance
# is less than this multiple of the direct distance.
RIDESHARE_MULTIPLIER = 1.1

# Time in minutes. Every taxi inside this radius counts as being 'the closest'.
INSTANT_DISPATCH_RADIUS = 1

# A passenger group of this size or larger will be willing to split in half if they
# can't find a ride within SPLIT_TIME minutes.
SPLIT_SIZE = 4

# Time in minutes a group of passengers will wait before splitting in half.
SPLIT_TIME = 5

# Q-learning parameter: learning rate.
ALPHA = 0.25

# Q-learning parameter: discount rate.
GAMMA = 0.9

# Q-learning parameter: maximum taxi size.
MAXSIZE = 16

# ----------------------------------------------------------------------------------------
# Derived parameters.
# ----------------------------------------------------------------------------------------

# Distance in meters a taxi can travel in one tick.
TICK_DIST = TAXI_SPEED * TICK_TIME

# Instant dispatch radius in meters.
INSTANT_DISPATCH_RANGE = TAXI_SPEED * INSTANT_DISPATCH_RADIUS * 60

# Per-tick probability of an idle taxi repositioning.
REPO_PROB = (1 / (MEAN_REPO_TIME * 60)) * TICK_TIME
