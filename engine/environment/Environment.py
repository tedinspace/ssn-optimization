from astropy import units 

from engine.environment.Scenario import Scenario
from engine.environment.StateCatalog import StateCatalog
from engine.environment.SatelliteTruth import SatelliteTruth
from engine.environment.sensors.Communication import SensorResponse
from engine.environment.bookkeeping.EventTracker import EventTracker, Event
from engine.builder.satellites.states import TLE_LIBRARY
from engine.builder.sensors.ssn import load_sensor_map


class Environment: 
    def __init__(self, sensor_keys, sat_keys, randomizer=None):
        ''''''
        self.randomizer = randomizer
        if self.randomizer:
            self.scenario_configs=Scenario(self.randomizer.get_epoch(), self.randomizer.get_scenario_length())   
        else:
            self.scenario_configs=Scenario()
        
        self.sensor_keys = sensor_keys
        self.sat_keys = sat_keys
       
        
    
    def reset(self):
        ''''''
        # randomize scenario
        if self.randomizer:
            self.scenario_configs=Scenario(self.randomizer.get_epoch(), self.randomizer.get_scenario_length())   
        
        self.satellite_truth = {}
        for i, key in enumerate(self.sat_keys):
            if self.randomizer:
                re_epoch = self.randomizer.get_state_reepoch()
            else:
                re_epoch=1.5
            self.satellite_truth[key] = SatelliteTruth(key, TLE_LIBRARY[key][1], TLE_LIBRARY[key][2], self.scenario_configs,re_epoch)
        
        self.unique_maneuvers  = 0
        if self.randomizer and self.randomizer.maneuver_details:
            k2M = self.randomizer.randomize_maneuvers(self.sat_keys, self.scenario_configs)
            for k in k2M:
                self.satellite_truth[k].add_maneuvers(k2M[k])
                self.unique_maneuvers +=len(k2M[k])
            #print(k2M)
            
        
        
        self.state_catalog = StateCatalog(self.satellite_truth)
        
        self.sensors =  load_sensor_map(self.sensor_keys, self.scenario_configs)
        
        self.tracker = EventTracker() 
        self.tracker.record_scenario(self.satellite_truth, self.sensors, self.scenario_configs)
        
        self.t = self.scenario_configs.scenario_epoch.copy()
        
        return self.t, self.state_catalog,[], False
        
    def step(self, actions):
        ''''''
        # 0. advance time
        self.t += units.s * self.scenario_configs.dt
        
        # 1. propagate truth
        for sat_key in self.satellite_truth:
            self.satellite_truth[sat_key].tick(self.t)
            
        # 2. pass tasks to sensor
        for agent in actions:
            if actions[agent]:
                self.tracker.record(Event.TASKING_ISSUED)
                sat_key = actions[agent][1]
                self.sensors[actions[agent][0]].pass_to_pipeine(self.t, agent, sat_key, self.state_catalog.current_catalog[sat_key]) 
                
        # 3. advance sensor operations
        for sensor_key in self.sensors:
            self.sensors[sensor_key].tick(self.t, self.satellite_truth)
            
        # 4. gather events
        events_out = []
        for sensor_key in self.sensors:
            response_messages = self.sensors[sensor_key].check_pipeline(self.t) 
            if response_messages:
                for message in response_messages:
                    self.tracker.record(message.response_type)
                    if (message.response_type == SensorResponse.CATALOG_STATE_UPDATE_MANEUVER 
                        or message.response_type == SensorResponse.CATALOG_STATE_UPDATE_NOMINAL):
                        self.state_catalog.update_state(message.sat_key, message.record)
                        self.tracker.record(Event.STATE_UPDATE)
                        self.tracker.record_state_update_info(message)
                        events_out.append(message)
                    if message.response_type == SensorResponse.FAILURE_OBJECT_LOST:
                        self.tracker.record_loss(message.sat_key)
                        
        return self.t, self.state_catalog, events_out, self.t > self.scenario_configs.scenario_end