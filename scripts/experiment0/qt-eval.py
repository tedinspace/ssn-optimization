
from engine.environment.Environment import Environment
from engine.agents.rl.QTableAgent import QTableAgent
from engine.environment.bookkeeping.SimOutcomeTracker import SimOutcomeTracker
from engine.util.plots import basic_ground_sensor_plot_v1, basic_uncertainty_plot
import pickle

N_ROUNDS =3

sat_keys = ["AEHF 2","AEHF 3", "AEHF 4"]
sensor_keys = ['mhr', 'socorro', 'boston']
env = Environment(sensor_keys, sat_keys)

sim_track = SimOutcomeTracker("q-table-eval",sensor_keys, sat_keys, N_ROUNDS)
#Agents = [QTableAgent("test agent",sensor_keys, sat_keys, env.scenario_configs )]



with open("./q-table-agent.pkl", "rb") as f:
    q_table_agent = pickle.load(f)
    
Agents = [q_table_agent]   
for i in range(N_ROUNDS):
    Agents[0].reset()
    env = Environment(sensor_keys, sat_keys) # TODO not ideal reset
    t, state_cat,events_out, Done = env.reset()
    TOTAL_REWARDS =0
    while Done ==False:
        # take actions
        actions = {}
        for agent in Agents:
            actions[agent.agent_id]=agent.decide(t, state_cat, evaluate=True) # <-always on policy
        # apply actions
        t, state_cat, events_out, Done = env.step(actions)
        
        # update agent
        TOTAL_REWARDS+= agent.update_q_table(t, state_cat, events_out, evaluate=True) #<-- won't change QT

    
    print("ROUND", i+1)
    print("REWARDS", TOTAL_REWARDS)
    sim_track.log_round(env,state_cat, TOTAL_REWARDS)


sim_track.save_instance('./'+sim_track.id+'.pkl')


basic_ground_sensor_plot_v1(env.tracker)
basic_uncertainty_plot(env.tracker)