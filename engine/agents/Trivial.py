
from engine.agents.Agent import Agent
import random

class RandomAgent(Agent):
    
    def __init__(self, agent_id, assigned_sensors, assigned_satellites ):
        super().__init__(agent_id, assigned_sensors, assigned_satellites)
                 
    def decide(self):
        #return super().do_nothing()
        if random.random() < .8:
            return super().do_nothing()
        return super().act_randomly()
    
    def reset(self):
        super().reset()
    
        
    