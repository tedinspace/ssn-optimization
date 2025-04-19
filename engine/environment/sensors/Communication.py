import random
from astropy import units
from enum import Enum

class SensorResponse(Enum):
    DROPPED_SENSOR_OFFLINE = "DROPPED_SENSOR_OFFLINE",  # Dropped due to sensor being offline.
    DROPPED_SCHEDULING = "DROPPED_SCHEDULING",  # Dropped due to scheduling issues.
    DROPPED_NOT_VISIBLE = "DROPPED_NOT_VISIBLE"  # Dropped due to the sensor not being visible.


class CommunicationPipeline:
    def __init__(self):
        ''' 
        Initializes the CommunicationPipeline 
        '''
        self.pending_incoming_task_messages = [] 
        self.pending_outgoing_messages = [] 
        
    def receive_task_request(self, time, agent_id, sat_key, frozen_state):
        ''' 
        Receive a task request and add it to the list of pending incoming task messages.
        
        Args:
            time (astropy.time.Time): The timestamp of when the request is received.
            agent_id (str): Identifier of the agent making the request.
            sat_key (str): Key associated with the satellite.
            frozen_state (StateCatalogEntry): The state entry of the satellite at the time of the request.
        '''
        self.pending_incoming_task_messages.append(PendingTaskMessage(agent_id, sat_key, time, frozen_state)) 
        
    def check_for_incoming_tasks(self, time):
        ''' 
        Checks for incoming tasks that are ready to be processed, based on the current time.
        
        Args:
            time (astropy.time.Time): The current time to compare against incoming task message arrival times.
        
        Returns:
            list: A list of `PendingTaskMessage` objects that are ready to be received.
        '''
        still_pending = []
        ready_to_receive = []
        
        for pending_task in self.pending_incoming_task_messages:
            if pending_task.arrival_time.mjd < time.mjd:
                ready_to_receive.append(pending_task)  # Task is ready for processing.
            else:
                still_pending.append(pending_task)  # Task is not yet ready.
                
        self.pending_incoming_task_messages = still_pending
        return ready_to_receive
    
    def drop_messages(self, reason, task_messages, time):
        ''' 
        Drop a list of task messages for a specific reason and record the response in the outgoing messages list.
        
        Args:
            reason (SensorResponse): The reason why the task message is being dropped.
            task_messages (list): A list of `PendingTaskMessage` objects to be dropped.
            time (astropy.time.Time): The current time to record in the response message.
        '''
        for message in task_messages:
            self.drop_message(reason, message, time)
    
    def drop_message(self, reason, task_message, time):
        ''' 
        Drop a single task message for a specific reason and record the response in the outgoing messages list.
        
        Args:
            reason (SensorResponse): The reason why the task message is being dropped.
            task_message (PendingTaskMessage): The task message to be dropped.
            time (astropy.time.Time): The current time to record in the response message.
        '''
        self.pending_outgoing_messages.append(ResponseMessage(reason, task_message, time)) 
        
    def check_for_outgoing_messages(self, time):
        ''' 
        Checks for outgoing response messages that are ready to be sent, based on the current time.
        
        Args:
            time (astropy.time.Time): The current time to compare against outgoing response message arrival times.
        
        Returns:
            list: A list of `ResponseMessage` objects that are ready to be sent.
        '''
        still_pending = []
        ready_to_receive = []
        
        for message in self.pending_outgoing_messages:
            if message.arrival_time.mjd < time.mjd:
                ready_to_receive.append(message)  # Response is ready to be sent.
            else:
                still_pending.append(message)  # Response is not yet ready.
                
        self.pending_outgoing_messages = still_pending
        return ready_to_receive
                
# -----------------------------------------------------------------------------------------
#                                           MESSAGES
# -----------------------------------------------------------------------------------------
class PendingTaskMessage:
    def __init__(self, agent_id, sat_key, issue_time, available_state):
        ''' 
        Initializes a PendingTaskMessage with the provided parameters.
        
        Args:
            agent_id (str): Identifier of the agent requesting the task.
            sat_key (str): Key associated with the satellite.
            issue_time (astropy.time.Time): The time the task was issued.
            available_state (StateCatalogEntry): The available state information for the task.
        '''
        
        self.available_state = available_state  
         
        self.agent_id = agent_id
        self.sat_key = sat_key 
        self.issue_time = issue_time
        self.arrival_time = randomize_message_delivery_time(issue_time)  # Randomized delivery time.
        
class ResponseMessage:
    def __init__(self, response_type, original_message, timestamp):
        ''' 
        Initializes a ResponseMessage with the response type and information from the original message.
        
        Args:
            response_type (SensorResponse): The type of response (reason for dropping).
            original_message (PendingTaskMessage): The original task message that was dropped.
            timestamp (astropy.time.Time): The time the response message was created.
        '''
        self.response_type = response_type
        
        self.agent_id = original_message.agent_id
        self.sat_key = original_message.sat_key
        self.issue_time = timestamp
        self.arrival_time = randomize_message_delivery_time(timestamp)  # Randomized delivery time for the response.

# -----------------------------------------------------------------------------------------
#                                          FUNCTIONS
# -----------------------------------------------------------------------------------------
def randomize_message_delivery_time(issue_time):
    ''' 
    Randomizes the message delivery time by adding a small random delay.
    
    Args:
        issue_time (astropy.time.Time): The time when the message is issued.
    
    Returns:
        astropy.time.Time: A new time with a random delay added.
    '''
    return issue_time + (5 + random.uniform(-2.5, 2.5)) * 60 * units.s  # Delay between -2.5 to 2.5 minutes.
