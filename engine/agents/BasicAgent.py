
import random

class BasicAgent:
    
    def __init__(self, agent_id, assigned_sensors, assigned_satellites ):
        self.agent_id = agent_id
        self.n_assigned_sensors = len(assigned_sensors)
        self.n_assigned_satellites = len(assigned_satellites)
        self.action_space_size = self.n_assigned_sensors*self.n_assigned_sensors + 1
        
        self.assigned_sensors = assigned_sensors
        self.assigned_satellites = assigned_satellites
        
        self.action_map = [None] # do nothing is index zero
        
        for sensor in self.assigned_sensors:
            for sat in self.assigned_satellites:
                self.action_map.append((sensor,sat))
                
    def decide(self):
        return self.action_map[random.randint(0, self.action_space_size-1)]
        
        
        
        