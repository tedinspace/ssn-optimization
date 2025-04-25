
from engine.environment.Environment import Environment
from engine.agents.Trivial import RandomAgent, DumbRandomAgent
from engine.agents.rl.QTableAgent import QTableAgent
from engine.agents.Algorithmic import BasicRevisitAgent
from engine.util.plots import basic_ground_sensor_plot_v1, basic_uncertainty_plot

sat_keys = ["AEHF 1","AEHF 2","AEHF 3", "AEHF 4"]
sensor_keys = ['mhr', 'socorro', 'boston']

env = Environment(sensor_keys, sat_keys)
Agents = [QTableAgent("test agent",sensor_keys, sat_keys, env.scenario_configs )]

t, state_cat, Done = env.reset()

while Done ==False:
    actions = {}
    for agent in Agents:
        actions[agent.agent_id]=agent.decide(t, state_cat)
    t, state_cat, Done = env.step(actions)


env.tracker.report_uncertainty(state_cat)
env.tracker.report()
#env.tracker.save_instance('./driver2.pkl')

basic_ground_sensor_plot_v1(env.tracker)
basic_uncertainty_plot(env.tracker)
