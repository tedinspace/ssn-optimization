from engine.agents.Base import AgentBaseSmarter
from engine.environment.Scenario import Scenario


class BasicRevisitAgent(AgentBaseSmarter):
    
    def __init__(self, agent_id, assigned_sensors, assigned_satellites, scenario_configs=Scenario()):
        super().__init__(agent_id, assigned_sensors, assigned_satellites, scenario_configs)
                 
    def decide(self, time, state_cat):
        
        #print(super().get_sensor_vm())
        #print(super().get_sat_vm())
        return [] 
    
    def reset(self):
        super().reset()