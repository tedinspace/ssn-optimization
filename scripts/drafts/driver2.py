
from engine.environment.Environment import Environment
from engine.agents.rl.QTableAgent import QTableAgent
from engine.util.plots import basic_ground_sensor_plot_v1, basic_uncertainty_plot

#sat_keys = ["AEHF 2","AEHF 3", "AEHF 4"]
#sensor_keys = ['mhr', 'socorro', 'boston']
sat_keys = ["AEHF 2","AEHF 3"]
sensor_keys = ["mhr"]


env = Environment(sensor_keys, sat_keys)
Agents = [QTableAgent("test agent",sensor_keys, sat_keys, env.scenario_configs )]

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

print(TOTAL_REWARDS)
#Agents[0].save('./q-table-test.pkl')
env.tracker.report_uncertainty(state_cat)
env.tracker.report()
#env.tracker.save_instance('./driver2.pkl')

basic_ground_sensor_plot_v1(env.tracker)
basic_uncertainty_plot(env.tracker)
