from enum import Enum


class Event(Enum):
    TASKING_ISSUED = "TASKING_ISSUED", 
    STATE_UPDATE = "STATE_UPDATE", 
    
    
class EventTracker:
    def __init__(self):
        self.event_counts = {}
        
    def record(self, event_type):
        '''event_type - Event enum '''
        if event_type in self.event_counts:
            self.event_counts[event_type] +=1
        else:
            self.event_counts[event_type]=1
    
    def report(self):
        for event_type in self.event_counts:
            print(str(event_type)+": "+str(self.event_counts[event_type]))
     
    
