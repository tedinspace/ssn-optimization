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
        
        self.sat_keys = set()
        self.sensor_keys = set()
        
        
        
    def record_scenario(self,sat_truth, sensor_truth):
        for sat_key in sat_truth:
            self.sat_keys.add(sat_key)
            self.maneuver_truth_record[sat_key]=sat_truth[sat_key].maneuvers
        for sensor_key in sensor_truth:
            self.sensor_keys.add(sensor_key)
            self.sensor_availability[sensor_key]= [sensor_truth[sensor_key].availability_trans_to_status , sensor_truth[sensor_key].availability_trans_times]
                  
         
    def record_tasking_interval(self,state_update_response):
        if not state_update_response.sensor_key in self.tasking_record:
            self.tasking_record[state_update_response.sensor_key]={}
        if not state_update_response.sat_key in self.tasking_record[state_update_response.sensor_key]:
            self.tasking_record[state_update_response.sensor_key][state_update_response.sat_key]=[]
        self.tasking_record[state_update_response.sensor_key][state_update_response.sat_key].append(state_update_response)

        
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
     
    
