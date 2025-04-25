
from engine.environment.Environment import Environment
from engine.agents.rl.QTableAgent import QTableAgent
from engine.environment.bookkeeping.SimOutcomeTracker import SimOutcomeTracker
from engine.util.plots import basic_ground_sensor_plot_v1, basic_uncertainty_plot

sat_keys = ["AEHF 2","AEHF 3", "AEHF 4"]
sensor_keys = ['mhr', 'socorro', 'boston']
env = Environment(sensor_keys, sat_keys)
N_ROUNDS =10

sim_track = SimOutcomeTracker("q-table-training",sensor_keys, sat_keys, N_ROUNDS)

Agents = [QTableAgent("test agent",sensor_keys, sat_keys, env.scenario_configs )]


for _ in range(N_ROUNDS):
    env = Environment(sensor_keys, sat_keys) # TODO not ideal
    t, state_cat,events_out, Done = env.reset()
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


    print("REWARDS", TOTAL_REWARDS)
    #
    #env.tracker.report_uncertainty(state_cat)
    #env.tracker.report()
    sim_track.log_round(env,state_cat, TOTAL_REWARDS)
#env.tracker.save_instance('./driver2.pkl')

#basic_ground_sensor_plot_v1(env.tracker)
#basic_uncertainty_plot(env.tracker)

Agents[0].save('./q-table-exp0.pkl')
sim_track.save_instance('./q-table-train-results0.pkl')