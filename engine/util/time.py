from astropy.time import Time
import numpy as np
# Constants for time units
SPD = 86400  # Seconds per day (1 day = 86400 seconds)
MPD = 1440   # Minutes per day (1 day = 1440 minutes)
HPD = 24     # Hours per day (1 day = 24 hours)

# Default time step for simulation or scenario updates in seconds
DEFAULT_DELTA_T = 30  # [S] - The default time step for updates, in seconds.

# Default epoch (start time) for scenarios
DEFAULT_SCENARIO_EPOCH = Time('2025-04-06 00:00:00.000', format='iso')

def seconds_between(t1, t2):
    return np.abs(t1.mjd - t2.mjd)*SPD