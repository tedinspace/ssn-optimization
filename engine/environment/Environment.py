from astropy import units 

from engine.environment.Scenario import Scenario
from engine.environment.StateCatalog import StateCatalog
from engine.environment.SatelliteTruth import SatelliteTruth, ManeuverDetails
from engine.environment.sensors.Communication import SensorResponse
from engine.environment.bookkeeping.EventTracker import EventTracker, Event
from engine.builder.satellites.states import TLE_LIBRARY
from engine.builder.sensors.ssn import load_sensor_map
from engine.util.time import  DEFAULT_SCENARIO_EPOCH

class Environment: 
    def __init__(self, sensor_keys, sat_keys):
        ''''''
        
        self.scenario_configs=Scenario(DEFAULT_SCENARIO_EPOCH, 24.0)
        
        self.sensor_keys = sensor_keys
        self.sat_keys = sat_keys
        
    
    def reset(self):
        ''''''
        self.satellite_truth = {}
        for i, key in enumerate(self.sat_keys):
            self.satellite_truth[key] = SatelliteTruth(key, TLE_LIBRARY[key][1], TLE_LIBRARY[key][2], self.scenario_configs, 13.3)
        
        self.satellite_truth[self.sat_keys[1]].add_maneuvers([ManeuverDetails(10, 1.5, self.scenario_configs), ManeuverDetails(15.3, 4.15, self.scenario_configs)])
        self.state_catalog = StateCatalog(self.satellite_truth)
        
        self.sensors =  load_sensor_map(self.sensor_keys, self.scenario_configs)
        
        self.tracker = EventTracker() 
        self.tracker.record_scenario(self.satellite_truth, self.sensors, self.scenario_configs)
        
        self.t = self.scenario_configs.scenario_epoch.copy()
        
        return self.t, self.state_catalog, False
        
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
        for sensor_key in self.sensors:
            response_messages = self.sensors[sensor_key].check_pipeline(self.t) 
            if response_messages:
                for message in response_messages:
                    self.tracker.record(message.response_type)
                    if message.response_type == SensorResponse.CATALOG_STATE_UPDATE_MANEUVER or message.response_type == SensorResponse.CATALOG_STATE_UPDATE_NOMINAL:
                        self.state_catalog.update_state(message.sat_key, message.record.orbit, message.record.orbit_validity_time)
                        self.tracker.record(Event.STATE_UPDATE)
                        self.tracker.record_tasking_interval(message)
                    if message.response_type == SensorResponse.FAILURE_OBJECT_LOST:
                        self.tracker.record_loss(message.sat_key)
                        
        return self.t, self.state_catalog, self.t > self.scenario_configs.scenario_end