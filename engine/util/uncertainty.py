import numpy as np
from engine.util.time import seconds_between

def gather_unseen_maneuvers(maneuvers_occurred, last_seen_time):
    '''list of ManeuverInfo objects and astropy Time time'''
    maneuvers_to_estimate = []
    for past_maneuver in maneuvers_occurred:
        if past_maneuver.time > last_seen_time:
            maneuvers_to_estimate.append(past_maneuver) 
    return maneuvers_to_estimate

def growth_1d(sigma_x,sigma_dx, dt ):
    return sigma_x*np.sqrt(1+((sigma_dx*dt)/sigma_x)**2)

def reestimate_1D(state_cat_entry, maneuvers, time_now):
    '''TODO - covariance standin'''
    sigma_x = state_cat_entry.sigma_X
    sigma_dx = state_cat_entry.sigma_dX
    
    validity_time = state_cat_entry.last_seen
    for m in maneuvers:
        dt = seconds_between(validity_time, m.time)
        sigma_dx = np.sqrt(sigma_dx**2 + m.magnitude_dv**2)
        #sigma_x = sigma_x*np.sqrt(1+((sigma_dx*dt)/sigma_x)**2)
        sigma_x = growth_1d(sigma_x, sigma_dx, dt)
        # for next round 
        validity_time = m.time
    
    
    return growth_1d(sigma_x, sigma_dx, seconds_between(validity_time, time_now))
    