
from engine.environment.Environment import Environment
from engine.environment.Randomizer import Randomizer
from engine.agents.Algorithmic import BasicRevisitAgent
from engine.agents.rl.QTableAgent import QTableAgent
from engine.environment.bookkeeping.SimOutcomeTracker import SimOutcomeTracker
from engine.util.plots import basic_ground_sensor_plot_v1, basic_uncertainty_plot
from engine.util.indexing import init_mapping
from engine.agents.rl.QTableAgent import  normalized_uncert_reward, compute_tasking_cost
from engine.util.time import mins_ago
from engine.environment.sensors.Communication import SensorResponse

EXPERIMENT_NAME = "S0"
N_ROUNDS = 1

sat_keys = ["AEHF 2"]
sensor_keys = ['mhr']
env = Environment(sensor_keys, sat_keys)


sim_track = SimOutcomeTracker("q-table-training",sensor_keys, sat_keys, N_ROUNDS)
Agents = [QTableAgent("test agent",sensor_keys, sat_keys)]
#Agents = [BasicRevisitAgent("revisit agent",sensor_keys, sat_keys)]

env = Environment(sensor_keys, sat_keys, randomizer=Randomizer(scenario_length_hrs=[6,6])) 
for i in range(N_ROUNDS):
    env.reset()
    t, state_cat,events_out, Done = env.reset()
    
    for i in range(len(Agents)):
        Agents[i].reset()
        if Agents[i].is_rl_agent:
             Agents[i].decay_eps()
                         
    
    TOTAL_REWARDS =0
    while Done ==False:
        # take actions
        actions = {}
        for agent in Agents:
            action = agent.decide(t, state_cat)
            actions[agent.agent_id] = action
            
        # apply actions
        t, state_cat, events_out, Done = env.step(actions)
        
        
        # update agent
        for agent in Agents:
            if agent.is_rl_agent:
                TOTAL_REWARDS+= agent.update_q_table(t, state_cat, events_out)

    #print(Agents[0].eps_threshold)
    print("ROUND", i+1)
    print("REWARDS", TOTAL_REWARDS)
    sim_track.log_round(env,state_cat, TOTAL_REWARDS)

env.tracker.report()
#env.tracker.save_instance('./driver2.pkl')

#sim_track.save_instance('./'+sim_track.id+'.pkl')
#Agents[0].save('./q-table-agent-'+EXPERIMENT_NAME+'.pkl')
#sim_track.save_instance('./q-table-train-results-exp0-v1.pkl')


basic_ground_sensor_plot_v1(env.tracker)
basic_uncertainty_plot(env.tracker)