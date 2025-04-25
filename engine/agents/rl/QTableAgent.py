from engine.agents.Base import AgentBaseSmarter
from engine.environment.Scenario import Scenario
from engine.environment.sensors.Communication import SensorResponse
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
    
    def update_q_table(self,state_keys, action_idx, value):
        V = self.get_action_values(state_keys)
        if len(V)==0:
            V = np.zeros(self.n_actions)
        V[action_idx]=value
        self.store_value(state_keys, V)
        
    def store_value(self,state_list, action_values):
        reduce(operator.getitem, state_list[:-1], self.q_table)[state_list[-1]] = action_values
    
     
        


class QTableAgent(AgentBaseSmarter):
    
    def __init__(self, agent_id, assigned_sensors, assigned_satellites, scenario_configs=Scenario()):
        super().__init__(agent_id, assigned_sensors, assigned_satellites, scenario_configs)
        self.agent_id = agent_id
        self.assigned_sensors = assigned_sensors
        self.assigned_satellites = assigned_satellites
        self.sat2index,self.index2sat = gen_index_maps(assigned_satellites)
        
        self.action_encoding = super().get_action_encoding()
        self.q_table = DynamicQTable(len(self.action_encoding))
        
        
        self.last_seen_states = [0, 30, 60, 90, 120, 150, 180, 210] # make this dynamic
        self.last_tasked_states = [-1, 30, 60, 90, 120, 150]
        
        self.last_tasked_times = init_mapping(self.assigned_satellites, None)
        
        # for update q-table
        self.cost_of_prev_action = 0
        self.prev_action_idx = None
        self.prev_state_keys = None

        
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
        
    def decide_onpolicy(self,state_keys):
        return  self.q_table.get_best_action(state_keys)
                 
    def decide(self, time, state_cat):
        # 1. discretize state
        state_keys = self.discretize_current_state(time, state_cat)
                
        # 2. select action
        action_idx = self.decide_onpolicy(state_keys)
        action = self.action_encoding[action_idx]
        # 3. action updates
        if action !=None:
            # i. compute cost of action 
            if self.last_tasked_times[action[1]]:
                m_ago = mins_ago(self.last_tasked_times[action[1]], time)
                self.cost_of_prev_action = compute_tasking_cost(m_ago)
            else: 
                self.cost_of_prev_action = 1
            
            
            # ii. update time since last task
            self.last_tasked_times[action[1]]=time
            
        else:
            self.cost_of_prev_action = 0
         
        
        
        self.prev_action_idx = action_idx
        self.prev_state_keys = state_keys
        
        return action
    
    def update_q_table(self, time, state_cat, events):
        # 1. costs: cost of previous action and TODO cost of state age? 
        cost = self.cost_of_prev_action
        
        # 2. rewards
        reward = 0
        for e in events:
            if e.agent_id == self.agent_id and (e.response_type == SensorResponse.CATALOG_STATE_UPDATE_MANEUVER 
                        or e.response_type == SensorResponse.CATALOG_STATE_UPDATE_NOMINAL):
                reward += normalized_uncert_reward(e)
        
        
        self.q_table.update_q_table(self.prev_state_keys, self.prev_action_idx, reward-cost)
          
    
    def reset(self):
        super().reset()
        self.last_tasked_times = init_mapping(self.assigned_satellites, None)
        self.cost_of_prev_action = 0
        self.prev_action_idx = None
        self.prev_state_keys = None
        
def normalized_uncert_reward(message):
    return  max(0, (message.record.sigma_X_at_acq-message.record.sigma_dX)/(message.record.task_length_mins*60))

def compute_tasking_cost(mins_ago, max_cost=25, min_cost=1, time_thresh_mins=35): # slope=max_cost-min)cost / (0-time_threshold_mins)
    if mins_ago > time_thresh_mins:
        return min_cost
    else:
        return (max_cost-min_cost)/(0-time_thresh_mins)*mins_ago + max_cost
    
    