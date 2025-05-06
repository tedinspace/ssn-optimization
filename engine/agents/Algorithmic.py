from engine.agents.Base import AgentBaseSmarter
from engine.environment.Scenario import Scenario
import random


class BasicRevisitAgent(AgentBaseSmarter):
    
    def __init__(self, agent_id, assigned_sensors, assigned_satellites, scenario_configs=Scenario(), revisit=90, task_buffer=20):
        self.assigned_sensors = assigned_sensors
        self.assigned_satellites = assigned_satellites
        self.last_tasked = {}
        self.is_rl_agent = False
        self.revisit_mins = revisit
        self.task_buffer_mins = task_buffer 
        super().__init__(agent_id, assigned_sensors, assigned_satellites, scenario_configs)
                 
    def decide(self, time, state_cat, evaluate=None):
        
        over_90 = []
        for sat in self.assigned_satellites:
            last_seen = (time.mjd - state_cat.current_catalog[sat].last_seen.mjd)*24*60
            
            if last_seen > self.revisit_mins: 
                if sat in self.last_tasked:
                    self.last_tasked
                    last_tasked = (time.mjd - self.last_tasked[sat].mjd)*24*60
                    if last_tasked > self.task_buffer_mins:
                        over_90.append(sat)
                else:
                    over_90.append(sat)
                    
        
        if over_90:
            sat = random.choice(over_90)
            sensor = list(super().get_sat_vm()[sat])
            if sensor:
                self.last_tasked[sat]=time
                return (random.choice(sensor),sat)
        
        return None 
    
    def reset(self):
        super().reset()
        self.last_tasked = {}