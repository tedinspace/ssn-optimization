from astropy.time import Time
from engine.util.time import HPD
from engine.util.astro import tle_to_orbit

class Satellite: 
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
        self.maneuvers = []
        self.n_maneuvers = 0
        self.n_maneuvers_occurred = 0

        