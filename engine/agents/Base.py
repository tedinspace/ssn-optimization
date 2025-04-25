import random
from engine.util.vis import generate_vis_map, vis_map_to_action_tuples
from engine.environment.Scenario import Scenario

class AgentBaseDumb:
    """
    Dumb agent base doesn't account for object vis
    """
    def __init__(self, agent_id, assigned_sensors, assigned_satellites):
        """
        Initialize the agent with its ID and assigned sensors/satellites.

        Parameters:
        - agent_id (int): Unique identifier for the agent.
        - assigned_sensors (list): List of sensors this agent can control.
        - assigned_satellites (list): List of satellites this agent can task.
        """
        self.agent_id = agent_id
        self.n_assigned_sensors = len(assigned_sensors)
        self.n_assigned_satellites = len(assigned_satellites)
        self.action_space_size = self.n_assigned_sensors * self.n_assigned_satellites + 1

        self.assigned_sensors = assigned_sensors
        self.assigned_satellites = assigned_satellites

        # Action 0 is always "do nothing", others are (sensor, satellite) pairs
        self.action_encoding = [None]
        for sensor in self.assigned_sensors:
            for sat in self.assigned_satellites:
                self.action_encoding.append((sensor, sat))

    def act_randomly(self):
        """
        Select a random action
        Returns:
        - None or (sensor_key, sat_key)
        """
        return self.action_encoding[random.randint(0, self.action_space_size - 1)]

    def do_nothing(self):
        """
        Return the "do nothing" action.
        Returns:
        - None
        """
        return None

    def reset(self):
        """
        Reset the agent's internal state.
        Currently a placeholder with no behavior.
        """
        pass


class AgentBaseSmarter:
    """
    agent builds a visibility map for its assigned sensors and satellites,
    allowing for more informed action encoding 
    """
    def __init__(self, agent_id, assigned_sensors, assigned_satellites, scenario_configs=Scenario()):
        """
        Initialize the agent with sensor/satellite assignments and visibility information.

        Parameters:
        - agent_id (int): Unique identifier for the agent.
        - assigned_sensors (list): List of sensors this agent can control.
        - assigned_satellites (list): List of satellites this agent can task.
        - scenario_configs (Scenario): Scenario object containing configuration details.
        """
        self.agent_id = agent_id
        self.n_assigned_sensors = len(assigned_sensors)
        self.n_assigned_satellites = len(assigned_satellites)
        self.assigned_sensors = assigned_sensors
        self.assigned_satellites = assigned_satellites

        # Generate visibility maps using helper function
        by_sensor, by_sat = generate_vis_map(assigned_sensors, assigned_satellites, scenario_configs)
        self.vis_map_sensor = by_sensor
        self.vis_map_sat = by_sat

        # Encode actions based on visibility information
        self.action_encoding = vis_map_to_action_tuples(self.vis_map_sensor)

        self.action_space_size = len(self.action_encoding)

    def get_sensor_vm(self):
        """
        Get the sensor-based visibility map.

        Returns:
        - dict: ([sensor_key]: set(sat_keys)) Visibility map keyed by sensor.
        """
        return self.vis_map_sensor

    def get_sat_vm(self):
        """
        Get the satellite-based visibility map.

        Returns:
        - dict: ([sat_key]: set(sensor_keys)) Visibility map keyed by satellite 
        """
        return self.vis_map_sat

    def act_randomly(self):
        """
        Select a random action based on visibility constraints.
        Returns:
        - A randomly selected action from the visibility-based action encoding.
        """
        return self.action_encoding[random.randint(0, self.action_space_size - 1)]

    def do_nothing(self):
        """
        Return the "do nothing" action.
        Returns:
        - None
        """
        return self.action_encoding[0]

    def reset(self):
        """
        Reset the agent's internal state.
        Currently a placeholder with no behavior.
        """
        pass
