from enum import Enum
import pickle


class Event(Enum):
    TASKING_ISSUED = "TASKING_ISSUED", 
    STATE_UPDATE = "STATE_UPDATE", 
    
    
class EventTracker:
    def __init__(self):
        self.event_counts = {}
        self.lost_objects = set()
        self.tasking_record = {}
        self.maneuver_truth_record = {}
        self.sensor_availability = {}
        
        self.uncertainty_trajs = {} # by object
        
        self.sat_keys = set()
        self.sensor_keys = set()
        
        self.scenario_configs = None
        
        
        
        
    def record_scenario(self,sat_truth, sensor_truth, scenario_configs):
        for sat_key in sat_truth:
            self.sat_keys.add(sat_key)
            self.maneuver_truth_record[sat_key]=sat_truth[sat_key].maneuvers
        for sensor_key in sensor_truth:
            self.sensor_keys.add(sensor_key)
            self.sensor_availability[sensor_key]= [sensor_truth[sensor_key].availability_trans_to_status , sensor_truth[sensor_key].availability_trans_times]
        self.scenario_configs = scenario_configs
                  
         
    def record_state_update_info(self,state_update_response):
        '''
            1. records successful tracking dirations
            2. 
        '''
        # 1. 
        if not state_update_response.sensor_key in self.tasking_record:
            self.tasking_record[state_update_response.sensor_key]={}
        if not state_update_response.sat_key in self.tasking_record[state_update_response.sensor_key]:
            self.tasking_record[state_update_response.sensor_key][state_update_response.sat_key]=[]
        self.tasking_record[state_update_response.sensor_key][state_update_response.sat_key].append(state_update_response)
        # 2. 
        if not state_update_response.sat_key in self.uncertainty_trajs:
            self.uncertainty_trajs[state_update_response.sat_key] = {}
            self.uncertainty_trajs[state_update_response.sat_key]['times']=[]
            self.uncertainty_trajs[state_update_response.sat_key]['sigma_X']=[]
        self.uncertainty_trajs[state_update_response.sat_key]['times'].append( state_update_response.record.scheduled_start.mjd)
        self.uncertainty_trajs[state_update_response.sat_key]['times'].append( state_update_response.record.orbit_validity_time.mjd)
        self.uncertainty_trajs[state_update_response.sat_key]['sigma_X'].append( state_update_response.record.sigma_X_at_acq)
        self.uncertainty_trajs[state_update_response.sat_key]['sigma_X'].append( state_update_response.record.sigma_X)
            
        

        
    def record(self, event_type):
        '''event_type - Event enum '''
        if event_type in self.event_counts:
            self.event_counts[event_type] +=1
        else:
            self.event_counts[event_type]=1
            
    def record_loss(self, sat_key):
        self.lost_objects.add(sat_key)
        
    
    def report(self):
        for event_type in self.event_counts:
            print(str(event_type)+": "+str(self.event_counts[event_type]))
        if self.lost_objects:
            print('loss: ')
            print(self.lost_objects)
            
    def save_instance(self, file_with_path):
        with open(file_with_path, "wb") as f:
            pickle.dump(self, f)
     
    
