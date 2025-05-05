
from engine.util.time import  DEFAULT_SCENARIO_EPOCH
from engine.util.random import u
import random as r

from astropy import units 


class Randomizer:
    def __init__(self, 
                 fixed_epoch=DEFAULT_SCENARIO_EPOCH,
                 epoch_stagger_hours = [0,24], 
                 scenario_length_hrs=[12,24],
                 reepoch_hrs = [0,1.0] 
                 
                 ):
        # scenario epoch and length
        self.fixed_epoch = fixed_epoch
        self.epoch_stagger_hrs = epoch_stagger_hours
        self.scenario_length_hrs = scenario_length_hrs
        # states
        self.reepoch_hrs = reepoch_hrs
        # maneuvers
        
        
        
        
    # ---------------------- SETTERS ----------------------
    #                          TODO
    # ---------------------- GETTERS ----------------------
    def get_epoch(self):
        return self.fixed_epoch + u(self.epoch_stagger_hrs, units.h)
    
    def get_scenario_length(self):
        return u(self.scenario_length_hrs)
    
    def get_state_reepoch(self):
        return u(self.reepoch_hrs)