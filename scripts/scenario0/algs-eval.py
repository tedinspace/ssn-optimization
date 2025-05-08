
from engine.environment.Environment import Environment
from engine.environment.Randomizer import Randomizer
from engine.agents.Algorithmic import BasicRevisitAgent
from engine.agents.Trivial import DoNothingAgent, RandomAgent
from engine.environment.bookkeeping.SimOutcomeTracker import SimOutcomeTracker
from engine.util.plots import basic_ground_sensor_plot_v1, basic_uncertainty_plot
import pickle

IS_DQN = False
EXPERIMENT_NAME = "S0"

BASE_PATH = './scripts/scenario0/'
N_ROUNDS = 1

sat_keys = ["AEHF 2"]
sensor_keys = ['mhr']

#AGENT = "revisit"
#Agents = [BasicRevisitAgent(AGENT,sensor_keys, sat_keys)]

#AGENT = "DN"
#Agents = [DoNothingAgent(AGENT,sensor_keys, sat_keys)]

#AGENT = "smart-random"
#Agents = [RandomAgent(AGENT,sensor_keys, sat_keys)]


#AGENT = "q-table"
#with open(BASE_PATH+"agent-q-table-S0.pkl", "rb") as f:
#    q_table_agent = pickle.load(f)
    
#Agents = [q_table_agent]  

IS_DQN = True
AGENT = "DQN"
with open(BASE_PATH+"agent-DQN-S0.pkl", "rb") as f:
    dqn_agent = pickle.load(f)
    
Agents = [dqn_agent]

sim_track = SimOutcomeTracker(EXPERIMENT_NAME+'-'+AGENT+"-eval",sensor_keys, sat_keys, N_ROUNDS)

env = Environment(sensor_keys, sat_keys, randomizer=Randomizer(scenario_length_hrs=[6,6])) 
for i in range(N_ROUNDS):
    t, state_cat,events_out, Done = env.reset()
    
    for j in range(len(Agents)):
        Agents[j].reset()
                         
    
    TOTAL_REWARDS =1
    while Done ==False:
        # take actions
        actions = {}
        for agent in Agents:
            action = agent.decide(t, state_cat, evaluate=True)
            actions[agent.agent_id] = action
            
        # apply actions
        t, state_cat, events_out, Done = env.step(actions)
        
        
        # update agent
        for agent in Agents:
            if agent.is_rl_agent:
                if not IS_DQN:
                    TOTAL_REWARDS+= agent.update_q_table(t, state_cat, events_out, evaluate=True)
                else:
                    TOTAL_REWARDS+= agent.update(t, state_cat, events_out, evaluate=True)

    #print(Agents[0].eps_threshold)
    print("ROUND", i+1)
    print("REWARDS", TOTAL_REWARDS)
    sim_track.log_round(env,state_cat, TOTAL_REWARDS)

env.tracker.report()
#sim_track.save_instance(BASE_PATH+sim_track.id+'.pkl')
#Agents[0].save('./q-table-agent-'+EXPERIMENT_NAME+'.pkl')


basic_ground_sensor_plot_v1(env.tracker)
basic_uncertainty_plot(env.tracker)