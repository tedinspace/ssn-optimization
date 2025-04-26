
from engine.environment.Environment import Environment
from engine.agents.rl.QTableAgent import QTableAgent
from engine.environment.bookkeeping.SimOutcomeTracker import SimOutcomeTracker
from engine.util.plots import basic_ground_sensor_plot_v1, basic_uncertainty_plot

N_ROUNDS =5

sat_keys = ["AEHF 2","AEHF 3", "AEHF 4"]
sensor_keys = ['mhr', 'socorro', 'boston']
env = Environment(sensor_keys, sat_keys)

sim_track = SimOutcomeTracker("q-table-training",sensor_keys, sat_keys, N_ROUNDS)
Agents = [QTableAgent("test agent",sensor_keys, sat_keys, env.scenario_configs )]


for i in range(N_ROUNDS):
    env = Environment(sensor_keys, sat_keys) # TODO not ideal reset
    t, state_cat,events_out, Done = env.reset()
    Agents[0].reset()
    Agents[0].decay_eps()
    TOTAL_REWARDS =0
    while Done ==False:
        # take actions
        actions = {}
        for agent in Agents:
            actions[agent.agent_id]=agent.decide(t, state_cat)
        # apply actions
        t, state_cat, events_out, Done = env.step(actions)
        
        # update agent
        TOTAL_REWARDS+= agent.update_q_table(t, state_cat, events_out)

    print(Agents[0].eps_threshold)
    print("ROUND", i+1)
    print("REWARDS", TOTAL_REWARDS)
    sim_track.log_round(env,state_cat, TOTAL_REWARDS)

#env.tracker.save_instance('./driver2.pkl')

sim_track.save_instance('./'+sim_track.id+'.pkl')
Agents[0].save('./q-table-agent.pkl')
#sim_track.save_instance('./q-table-train-results-exp0-v1.pkl')


basic_ground_sensor_plot_v1(env.tracker)
basic_uncertainty_plot(env.tracker)