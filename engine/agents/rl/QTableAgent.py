from engine.agents.Base import AgentBaseSmarter
from engine.environment.Scenario import Scenario
from engine.util.indexing import gen_index_maps, dynamic_dict, init_mapping
from engine.util.time import mins_ago
from functools import reduce
import operator
import numpy as np

class DynamicQTable:
    def __init__(self, n_actions):
        self.q_table = dynamic_dict()
        self.n_actions = n_actions
        
    def get_action_values(self, state_list):
        return reduce(operator.getitem, state_list, self.q_table)
    
    def get_best_action(self,state_list):
        V = self.get_action_values(state_list)
        if len(V)==0:
            V = np.zeros(self.n_actions)
            self.store_value(state_list, V)
        return np.random.choice(np.where(V == np.max(V))[0])
        
    
    def store_value(self,state_list, action_values):
        reduce(operator.getitem, state_list[:-1], self.q_table)[state_list[-1]] = action_values
    
     
        


class QTableAgent(AgentBaseSmarter):
    
    def __init__(self, agent_id, assigned_sensors, assigned_satellites, scenario_configs=Scenario()):
        super().__init__(agent_id, assigned_sensors, assigned_satellites, scenario_configs)

        self.assigned_sensors = assigned_sensors
        self.assigned_satellites = assigned_satellites
        self.sat2index,self.index2sat = gen_index_maps(assigned_satellites)
        
        self.action_encoding = super().get_action_encoding()
        self.q_table = DynamicQTable(len(self.action_encoding))
        
        

        self.last_seen_states = [0, 30, 60, 90, 120, 150, 180, 210] # make this dynamic
        self.last_tasked_states = [-1, 30, 60, 90, 120, 150]
        
        
        
        self.last_tasked_times = init_mapping(self.assigned_satellites, None)

        
    def discretize_current_state(self, time, state_cat):
        
        state_keys = []
        for sat_key in self.assigned_satellites:
            
            # 1. how long ago was satellite seen
            m_ago = mins_ago(state_cat.current_catalog[sat_key].last_seen, time)
            state_keys.append(min(self.last_seen_states, key=lambda t: abs(t - m_ago)))
            
            # 2. how long ago was satellite tasked
            if self.last_tasked_times[sat_key]:
                m_ago = mins_ago(self.last_tasked_times[sat_key], time)
                state_keys.append(min(self.last_tasked_states, key=lambda t: abs(t - m_ago)))
            else:
                state_keys.append(-1)
                
        return state_keys
        
    def decide_onpolicy(self,time,state_cat):
        # 1. discretize state
        state_keys = self.discretize_current_state(time,state_cat)    
        # 2. choose best action
        return self.action_encoding[self.q_table.get_best_action(state_keys)]
                 
    def decide(self, time, state_cat):
  
                
        # 2. select action
        action = self.decide_onpolicy(time,state_cat)

        # 3. update last tasked for object (if applicable)
        if action !=None:
            self.last_tasked_times[action[1]]=time
         

        
        return action
    
    def reset(self):
        super().reset()
        self.last_tasked_times = init_mapping(self.assigned_satellites, None)
            
        
        
        
