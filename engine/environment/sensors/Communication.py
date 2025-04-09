import random
from astropy import units 
from enum import Enum

class SensorResponse(Enum):
    DROPPED_SENSOR_OFFLINE = "DROPPED_SENSOR_OFFLINE",
    DROPPED_SCHEDULING = "DROPPED_SCHEDULING",
    DROPPED_NOT_VISIBLE = "DROPPED_NOT_VISIBLE"

class CommunicationPipeline:
    def __init__(self):
        self.pending_incoming_task_messages = []
        self.pending_outgoing_messages = []
        
        
    def receive_task_request(self, time, agent_id, sat_key, frozen_state):
        self.pending_incoming_task_messages.append(PendingTaskMessage(agent_id, sat_key, time, frozen_state)) 
        
    def check_for_incoming_tasks(self, time):
        still_pending = []
        ready_to_receive = []
        
        for pending_task in self.pending_incoming_task_messages:
            if pending_task.arrival_time.mjd < time.mjd:
                ready_to_receive.append(pending_task)
            else:
                still_pending.append(pending_task)
                
        self.pending_incoming_task_messages = still_pending
        return ready_to_receive
    
    def drop_messages(self, reason, task_messages, time):
        for message in task_messages:
            self.drop_message(reason, message, time)
    
    def drop_message(self, reason, task_message, time):
        self.pending_outgoing_messages.append(ResponseMessage(reason, task_message, time)) 
        
    def check_for_outgoing_messages(self,time):
        still_pending = []
        ready_to_receive = []
        for message in self.pending_outgoing_messages:
            if message.arrival_time.mjd < time.mjd: 
                ready_to_receive.append(message)
            else:
                still_pending.append(message)
        self.pending_outgoing_messages = still_pending
        return ready_to_receive
                
    
    
             
class PendingTaskMessage:
    def __init__(self, agent_id, sat_key, issue_time, available_state):
        self.agent_id = agent_id
        self.sat_key = sat_key 
        self.issue_time = issue_time
        self.available_state = available_state   
        self.arrival_time = randomize_message_delivery_time(issue_time) 
        
class ResponseMessage:
    def __init__(self, response_type, original_message, timestamp):
        self.response_type = response_type
        self.agent_id = original_message.agent_id
        self.sat_key = original_message.agent_id
        self.issue_time = timestamp
        self.arrival_time = randomize_message_delivery_time(timestamp)         

def randomize_message_delivery_time(issue_time):
    return issue_time + (5 + random.uniform(-2.5, 2.5))*60*units.s