
from engine.environment.Environment import Environment
from engine.environment.Randomizer import Randomizer
from engine.agents.rl.QTableAgent import QTableAgent
from engine.environment.bookkeeping.SimOutcomeTracker import SimOutcomeTracker
from engine.util.plots import basic_ground_sensor_plot_v1, basic_uncertainty_plot


EXPERIMENT_NAME = "S4"

BASE_PATH = './scripts/scenario4/'
N_ROUNDS = 100

sat_keys = ["AEHF 1", "AEHF 2", "AEHF 3", "AEHF 4", "MUOS", "MUOS 3", "MUOS 5", "GOES 1", "GOES 5", "GOES 6", "GOES 7", "AMC 3"]
sensor_keys = ['mhr', 'ascension', 'socorro', 'vandenberg']
env = Environment(sensor_keys, sat_keys)


AGENT = "q-table"
Agents = [QTableAgent("AGENT",sensor_keys, sat_keys, env.scenario_configs, cost_scale=100 )]


sim_track = SimOutcomeTracker(EXPERIMENT_NAME+'-'+AGENT+"-train",sensor_keys, sat_keys, N_ROUNDS)

env = Environment(sensor_keys, sat_keys, randomizer=Randomizer(scenario_length_hrs=[24,24], 
                                                              maneuver_details=["type1", [3,6], [1,2], [0.5,11]])) 
for i in range(N_ROUNDS):
    env.reset()
    t, state_cat,events_out, Done = env.reset()
    
    for j in range(len(Agents)):
        Agents[j].reset()
        if Agents[j].is_rl_agent:
             Agents[j].decay_eps()
             print('eps-threshold',  Agents[j].eps_threshold)
                         
    
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
sim_track.save_instance(BASE_PATH+sim_track.id+'.pkl')
Agents[0].save(BASE_PATH+'agent-'+AGENT+'-'+EXPERIMENT_NAME+'.pkl')


basic_ground_sensor_plot_v1(env.tracker)
basic_uncertainty_plot(env.tracker)