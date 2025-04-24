
from engine.environment.Environment import Environment
from engine.agents.Trivial import RandomAgent
from engine.util.plots import basic_ground_sensor_plot_v1, basic_uncertainty_plot

sat_keys = ["AEHF 1","AEHF 2","AEHF 3", "AEHF 4"]
sensor_keys = ['mhr', 'socorro', 'boston']
Agents = [RandomAgent("test agent",sensor_keys, sat_keys )]

env = Environment(sensor_keys, sat_keys)
t, state_cat, Done = env.reset()

while Done ==False:
    actions = {}
    for agent in Agents:
        actions[agent.agent_id]=agent.decide()
    t, state_cat, Done = env.step(actions)


#env.tracker.save_instance('./driver2.pkl')
basic_ground_sensor_plot_v1(env.tracker)
basic_uncertainty_plot(env.tracker)
