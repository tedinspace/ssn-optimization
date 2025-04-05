import random
import numpy as np
from astropy.time import Time
from astropy import units 
from poliastro.maneuver import Maneuver
from engine.util.time import HPD
from engine.util.astro import tle_to_orbit

class SatelliteTruth: 
    def __init__(self, name, l1, l2, scenario_configs, reepoch_hours=None):
        # information
        self.name = name
        self.l1 = l1
        self.l2 = l2
        
        # time stuff
        self.scenario_epoch = scenario_configs.scenario_epoch
        self.is_reepoched = False 
        self.reepoch_hours = None
        self.reepoch = None
        if reepoch_hours != None:
            self.is_reepoched = True
            self.reepoch_hours = reepoch_hours
            self.reepoch = Time( self.scenario_epoch.mjd - reepoch_hours/HPD, format='mjd')

        # state stuff 
        self.orbit = tle_to_orbit(l1, l2, self.reepoch)
        
        # maneuver stuff 
        self.n_maneuvers = 0
        self.maneuvers_occurred = []
        self.maneuvers_remaining = []
        
    def add_maneuvers(self, maneuver_list):
        self.maneuvers_occurred = []
        self.maneuvers_remaining = maneuver_list
        self.n_maneuvers = len(maneuver_list)

    def tick(self, t):
        ''' t - astropy.time.core.Time'''
        # maneuver estimation
        remaining = []
        for m in self.maneuvers_remaining:
            if m.time <= t:
                # return to the time of the maneuver
                m.occurred = True
                self.orbit = self.orbit.propagate(m.time).apply_maneuver( Maneuver.impulse( m.maneuver << (units.m / units.s)))
                self.maneuvers_occurred.append(m)
            else:
                remaining.append(m)
        self.maneuvers_remaining = remaining
        # propagate to current time
        self.orbit = self.orbit.propagate(t) 
        
        
        
class ManeuverDetails:
    def __init__(self,magnitude_dv, hours_into_scenario, scenario_configs):
        self.dir = np.array([random.random(), random.random(),random.random()])
        self.dir = self.dir/np.sum(self.dir) # normalize
        self.maneuver = self.dir * magnitude_dv
        self.time = scenario_configs.scenario_epoch + hours_into_scenario * units.h
        self.occurred = False