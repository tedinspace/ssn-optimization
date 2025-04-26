from engine.agents.Trivial import DoNothingAgent, RandomAgent
from engine.agents.Algorithmic import BasicRevisitAgent
from engine.agents.rl.QTableAgent import  normalized_uncert_reward, compute_tasking_cost

from engine.environment.Environment import Environment
from engine.environment.bookkeeping.SimOutcomeTracker import SimOutcomeTracker
from engine.util.plots import basic_ground_sensor_plot_v1, basic_uncertainty_plot
from engine.environment.sensors.Communication import SensorResponse
from engine.util.indexing import init_mapping
from engine.util.time import mins_ago

N_ROUNDS =100

sat_keys = ["AEHF 2","AEHF 3", "AEHF 4"]
sensor_keys = ['mhr', 'socorro', 'boston']
env = Environment(sensor_keys, sat_keys)

# > do nothing 
#sim_track = SimOutcomeTracker("dn-eval-exp0",sensor_keys, sat_keys, N_ROUNDS)
#Agents = [DoNothingAgent("test agent",sensor_keys, sat_keys )]

# > pure random 
#sim_track = SimOutcomeTracker("pure-r-eval-exp0",sensor_keys, sat_keys, N_ROUNDS)
#Agents = [RandomAgent("test agent",sensor_keys, sat_keys,do_nothing_rate=0 )]

# > restrained random 
#sim_track = SimOutcomeTracker("rest-r-eval-exp0",sensor_keys, sat_keys, N_ROUNDS)
#Agents = [RandomAgent("test agent",sensor_keys, sat_keys )]

# > basic revisit 
sim_track = SimOutcomeTracker("revisit-alg-exp0",sensor_keys, sat_keys, N_ROUNDS)



print(sim_track.id)
for i in range(N_ROUNDS):
    env = Environment(sensor_keys, sat_keys) # TODO not ideal reset
    t, state_cat,events_out, Done = env.reset()
    TOTAL_REWARDS =0
    
    time_last_tasked = init_mapping(sat_keys, None)
    Agents = [BasicRevisitAgent("test agent",sensor_keys, sat_keys )]
    
    while Done ==False:
        # take actions
        actions = {}
        for agent in Agents:
            action = agent.decide(t, state_cat)
            actions[agent.agent_id] = action
            if action !=None:
                if time_last_tasked[action[1]] != None:
                    TOTAL_REWARDS-= compute_tasking_cost(mins_ago(time_last_tasked[action[1]], t))
                    
                else:
                    TOTAL_REWARDS-=1
                    
                time_last_tasked[action[1]] = t
                    
                
        # apply actions
        t, state_cat, events_out, Done = env.step(actions)
        
        for e in events_out:
            if (e.response_type == SensorResponse.CATALOG_STATE_UPDATE_MANEUVER 
                        or e.response_type == SensorResponse.CATALOG_STATE_UPDATE_NOMINAL):
                TOTAL_REWARDS+=normalized_uncert_reward(e)
                
        
        # update agent
        #TOTAL_REWARDS+= agent.update_q_table(t, state_cat, events_out)

    print("ROUND", i+1)
    print("REWARDS", TOTAL_REWARDS)
    sim_track.log_round(env,state_cat, TOTAL_REWARDS)


sim_track.save_instance('./'+sim_track.id+'.pkl')


basic_ground_sensor_plot_v1(env.tracker)
basic_uncertainty_plot(env.tracker)