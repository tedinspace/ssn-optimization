import random
from engine.util.vis import generate_vis_map, vis_map_to_action_tuples

class AgentBaseDumb:
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
        return self.action_encoding[random.randint(0, self.action_space_size-1)] 
    
    def do_nothing(self):
        return self.action_encoding[0]
    
    def reset(self):
        pass
    
        
        
class AgentBaseSmarter:
    def __init__(self, agent_id, assigned_sensors, assigned_satellites ):
        self.agent_id = agent_id
        self.n_assigned_sensors = len(assigned_sensors)
        self.n_assigned_satellites = len(assigned_satellites)
        self.assigned_sensors = assigned_sensors
        self.assigned_satellites = assigned_satellites
        
        self.vis_map = generate_vis_map(assigned_sensors, assigned_satellites)

        self.action_encoding = vis_map_to_action_tuples(self.vis_map)
                
        self.action_space_size = len(self.action_encoding)
        
        
    def act_randomly(self):
        return self.action_encoding[random.randint(0, self.action_space_size-1)] 
    
    def do_nothing(self):
        return self.action_encoding[0]
    
    def reset(self):
        pass
    
    

                    