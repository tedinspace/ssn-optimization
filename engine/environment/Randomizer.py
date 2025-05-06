
from engine.util.time import  DEFAULT_SCENARIO_EPOCH
from engine.util.random import u
import random as r
from engine.environment.SatelliteTruth import SatelliteTruth, ManeuverDetails

from astropy import units 


class Randomizer:
    def __init__(self, 
                 fixed_epoch=DEFAULT_SCENARIO_EPOCH,
                 epoch_stagger_hours = [0,24], 
                 scenario_length_hrs=[12,24],
                 reepoch_hrs = [0,1.0],
                 maneuver_details = None, 
                 #maneuver_details = ["type1", [0,1], [1,2], [0.5,5]]
                 
                 ):
        # scenario epoch and length
        self.fixed_epoch = fixed_epoch
        self.epoch_stagger_hrs = epoch_stagger_hours
        self.scenario_length_hrs = scenario_length_hrs
        # states
        self.reepoch_hrs = reepoch_hrs
        # maneuvers
        self.maneuver_details = maneuver_details
        
        
        
        
    # ---------------------- SETTERS ----------------------
    #                          TODO
    # ---------------------- GETTERS ----------------------
    def get_epoch(self):
        return self.fixed_epoch + u(self.epoch_stagger_hrs, units.h)
    
    def get_scenario_length(self):
        return u(self.scenario_length_hrs)
    
    def get_state_reepoch(self):
        return u(self.reepoch_hrs)
    
    def randomize_maneuvers(self, sat_keys, scenario_configs):
        #["type1", [0,1], [1,2], [0.5,11]]
        k2M = {}
        if self.maneuver_details:
            if self.maneuver_details[0]=="type1":
                
                n_objects_range =  self.maneuver_details[1]
                n_maneuvers_per_object_range = self.maneuver_details[2]
                delta_v_range = self.maneuver_details[3]
                
                n_objects = r.randint(n_objects_range[0], n_objects_range[1])
                sat_keys_man = r.sample(sat_keys, n_objects)
                
                L_hrs = scenario_configs.scenario_length_hours
                for sk in sat_keys_man:
                    M = []
                    n_man = r.randint(n_maneuvers_per_object_range[0], n_maneuvers_per_object_range[1])
         
                    for i in range(n_man):
                        mag = r.uniform(delta_v_range[0], delta_v_range[1])
                        timing = r.uniform(0.0001,L_hrs*.75 )
                        M.append(ManeuverDetails(mag, timing, scenario_configs))
                    if len(M)>0:
                        k2M[sk]=M
                
        
        
        return k2M