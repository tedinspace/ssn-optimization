from engine.agents.Base import AgentBaseSmarter
from engine.agents.rl.QTableAgent import compute_tasking_cost, normalized_uncert_reward
from engine.environment.Scenario import Scenario
from engine.environment.sensors.Communication import SensorResponse
from engine.util.indexing import gen_index_maps, dynamic_dict, init_mapping
from engine.util.time import mins_ago
from functools import reduce
import operator
import numpy as np
import random
import pickle
import torch
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import random
import numpy as np
from collections import deque


learning_rate = 0.001
gamma = 0.99
batch_size = 64
target_update_freq = 1000
memory_size = 10000
episodes = 1000



class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, output_dim)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return F.softmax(x, dim=-1)  


class DQNAgent(AgentBaseSmarter):
    
    def __init__(self, agent_id, assigned_sensors, assigned_satellites, scenario_configs=Scenario(), 
                 epsilon=1, epsilon_dec=0.995, epsilon_min=0.01, cost_scale = 100,
                 ):
        super().__init__(agent_id, assigned_sensors, assigned_satellites, scenario_configs)
        self.is_rl_agent = True
        self.agent_id = agent_id
        self.assigned_sensors = assigned_sensors
        self.assigned_satellites = assigned_satellites
        self.sat2index,self.index2sat = gen_index_maps(assigned_satellites)
        
        self.action_encoding = super().get_action_encoding()
        
        self.last_tasked_times = init_mapping(self.assigned_satellites, None)
        
        # -----------------------------------------------
        
        self.state_size = 2*len(self.assigned_satellites) # TODO 
        self.action_size = len(self.action_encoding)
        
        self.input_dim = self.state_size
        self.output_dim = self.action_size
        
        self.policy_net = DQN(self.input_dim, self.output_dim)
        self.target_net = DQN(self.input_dim, self.output_dim)
        
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)   
        self.memory = deque(maxlen=memory_size)
        
        
        # -----------------------------------------------
        # for update q-table
        self.cost_of_prev_action = 0
        self.prev_action_idx = None
        self.prev_state = None
        
        # training
        self.epsilon = epsilon
        self.eps_threshold = epsilon
        self.epsilon_dec = epsilon_dec
        self.epsilon_min = epsilon_min
        
        self.cost_scale = cost_scale
        
        
    def save(self, file_with_path):
        with open(file_with_path, "wb") as f:
            pickle.dump(self, f)
        
    def reset(self):
            super().reset()
            self.last_tasked_times = init_mapping(self.assigned_satellites, None)
            self.cost_of_prev_action = 0
            self.prev_action_idx = None
            self.prev_state = None
    def remember(self, state, reward, next_state, done):

        if self.prev_action_idx!=None:
            self.memory.append((state, self.prev_action_idx, reward, next_state, done))
        
    def decide_onpolicy(self, state):
        state = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            action_probs = self.policy_net(state).squeeze(0) 
        return torch.multinomial(action_probs, 1).item()
    
    def encode_state(self, time, state_cat):
        
        state = []
        for sat_key in self.assigned_satellites:
            
            # 1. how long ago was satellite seen
            state.append( mins_ago(state_cat.current_catalog[sat_key].last_seen, time)/3600)
            
            # 2. how long ago was satellite tasked
            if self.last_tasked_times[sat_key]:
                state.append(mins_ago(self.last_tasked_times[sat_key], time)/3600) # normalized to fraciton of day
            else:
                state.append(-1)
                
        return state
        
                 
    def decide(self, time, state_cat, evaluate=False):
        state = self.encode_state(time, state_cat)
        if not evaluate: # training
            # 2. select action
            if random.random() <  self.eps_threshold :
                if random.random() < 0.8:
                    action_idx = 0
                else:
                    action_idx = super().act_randomly_idx()
                    
            else:
                action_idx = self.decide_onpolicy(state)
        else: # evaluatino
            action_idx = self.decide_onpolicy(state)
            
            
            
        
        # 3. action updates
        action = self.action_encoding[action_idx]
        if action !=None:
            # i. compute cost of action 
            if self.last_tasked_times[action[1]]:
                m_ago = mins_ago(self.last_tasked_times[action[1]], time)
                self.cost_of_prev_action = compute_tasking_cost(m_ago)
                #self.cost_of_prev_action = 0
            else: 
                self.cost_of_prev_action = 0.005
            
            # ii. update time since last task
            self.last_tasked_times[action[1]]=time
            
        else:
            self.cost_of_prev_action = 0
         
        
        
        self.prev_action_idx = action_idx
        self.prev_state = state
        return action
    
    def decay_eps(self):
        self.eps_threshold = max(self.epsilon_min, self.eps_threshold * self.epsilon_dec)
    
    def update_target(self,steps):
        if steps % target_update_freq == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
            
    def update(self, time, state_cat, events, evaluate=False):
        # 1. costs: cost of previous action and TODO cost of state age? 
        cost = self.cost_of_prev_action/self.cost_scale
                
        # 2. rewards
        reward = 0
        for e in events:
            if e.agent_id == self.agent_id and (e.response_type == SensorResponse.CATALOG_STATE_UPDATE_MANEUVER 
                        or e.response_type == SensorResponse.CATALOG_STATE_UPDATE_NOMINAL):
                reward += normalized_uncert_reward(e)
        
        if evaluate == False:
            self.optimize_model()
            
        return reward-cost        
            
    def optimize_model(self):
        if len(self.memory) < batch_size:
            return
        
        batch = random.sample(self.memory, batch_size)
        state_batch, action_batch, reward_batch, next_state_batch, done_batch = zip(*batch)
        
        state_batch = torch.FloatTensor(state_batch)
        action_batch = torch.LongTensor(action_batch).unsqueeze(1)
        reward_batch = torch.FloatTensor(reward_batch)
        next_state_batch = torch.FloatTensor(next_state_batch)
        done_batch = torch.FloatTensor(done_batch)
        
        q_values = self.policy_net(state_batch).gather(1, action_batch).squeeze()
        
        with torch.no_grad():
            max_next_q_values = self.target_net(next_state_batch).max(1)[0]
            target_q_values = reward_batch + gamma * max_next_q_values * (1 - done_batch)
        loss = nn.MSELoss()(q_values, target_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        