
from engine.agents.Agent import Agent
import random

class DumbRandomAgent(Agent):
    
    def __init__(self, agent_id, assigned_sensors, assigned_satellites, do_nothing_rate=0.8 ):
        super().__init__(agent_id, assigned_sensors, assigned_satellites)
        self.do_nothing_rate = do_nothing_rate
                 
    def decide(self):
        #return super().do_nothing()
        if random.random() < self.do_nothing_rate:
            return super().do_nothing()
        return super().act_randomly()
    
    def reset(self):
        super().reset()
    
        
    