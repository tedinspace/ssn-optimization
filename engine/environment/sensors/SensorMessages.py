
class PendingTaskMessage:
    def __init__(self, agent_id, sat_key, arrial_time, available_state):
        self.agent_id = agent_id
        self.sat_key = sat_key 
        self.arrial_time = arrial_time 
        self.available_state = available_state