import random

class Agent:
    def __init__(self, agent_id, assigned_sensors,assigned_satellites ):
        self.agent_id = agent_id
        self.n_assigned_sensors = len(assigned_sensors)
        self.n_assigned_satellites = len(assigned_satellites)
        self.action_space_size = self.n_assigned_sensors*self.n_assigned_satellites + 1
        
        self.assigned_sensors = assigned_sensors
        self.assigned_satellites = assigned_satellites
        
        # action 0 will always be do-nothing; >0 (sensor,sat) tuple 
        self.action_encoding = [None] 
        for sensor in self.assigned_sensors:
            for sat in self.assigned_satellites:
                self.action_encoding.append((sensor,sat))
                
    def act_randomly(self):
        '''acts randomly (won't pick action=0/do nothing)'''
        return self.action_encoding[random.randint(1, self.action_space_size-1)] 
    
    def do_nothing(self):
        return self.action_encoding[0]
    
    def reset(self):
        # TODO
        return
        
        
        