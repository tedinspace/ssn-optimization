
from engine.environment.Environment import Environment
from engine.environment.Randomizer import Randomizer
from engine.agents.rl.DQNAgent import DQNAgent
from engine.environment.bookkeeping.SimOutcomeTracker import SimOutcomeTracker
from engine.util.plots import basic_ground_sensor_plot_v1, basic_uncertainty_plot


EXPERIMENT_NAME = "S0"

BASE_PATH = './scripts/scenario0/'
N_ROUNDS = 100

sat_keys = ["AEHF 2"]
sensor_keys = ['mhr']
env = Environment(sensor_keys, sat_keys)


AGENT = "DQN"
Agents = [DQNAgent(AGENT, sensor_keys, sat_keys, env.scenario_configs, cost_scale=1/3 )]


sim_track = SimOutcomeTracker(EXPERIMENT_NAME+'-'+AGENT+"-train",sensor_keys, sat_keys, N_ROUNDS)

env = Environment(sensor_keys, sat_keys, randomizer=Randomizer(scenario_length_hrs=[12,12])) 

for i in range(N_ROUNDS):
    t, state_cat,events_out, Done = env.reset()
    
   
                         
    
    TOTAL_REWARDS =0
    steps_done = 0
    state = Agents[0].encode_state(t, state_cat)
    
    while Done ==False:
        # take actions
        actions = {}
        for agent in Agents:
            action = agent.decide(t, state_cat)
            actions[agent.agent_id] = action
            
        # apply actions
        t, state_cat, events_out, Done = env.step(actions)
        
        
        reward_round = 0
        # update agent
        for agent in Agents:
            if agent.is_rl_agent:
                reward_round+= agent.update(t, state_cat, events_out)
                
                next_state = agent.encode_state(t, state_cat)
                
                agent.remember(state, reward_round, next_state, Done)
                agent.update_target(steps_done)
                TOTAL_REWARDS+=reward_round
                    
        state = next_state
        steps_done+=1

    for j in range(len(Agents)):
        Agents[j].reset()
        if Agents[j].is_rl_agent:
            Agents[j].decay_eps()
            print('eps-threshold',  Agents[j].eps_threshold)
            
    #print(Agents[0].eps_threshold)
    print("ROUND", i+1)
    print("REWARDS", TOTAL_REWARDS)
    sim_track.log_round(env,state_cat, TOTAL_REWARDS)

env.tracker.report()
sim_track.save_instance(BASE_PATH+sim_track.id+'.pkl')
Agents[0].save(BASE_PATH+'agent-'+AGENT+'-'+EXPERIMENT_NAME+'.pkl')


basic_ground_sensor_plot_v1(env.tracker)
basic_uncertainty_plot(env.tracker)