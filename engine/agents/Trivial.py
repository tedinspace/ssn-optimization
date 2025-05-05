from engine.agents.Base import AgentBaseDumb, AgentBaseSmarter
import random


class DoNothingAgent(AgentBaseDumb):
    """
        Does nothing
    """
    
    def __init__(self, agent_id, assigned_sensors, assigned_satellites):
        super().__init__(agent_id, assigned_sensors, assigned_satellites)
        self.is_rl_agent = False

    def decide(self, *args, **kwargs):
        """
        Always does nothing

        Returns:
        - None
        """
        return super().do_nothing()
    
    def reset(self):
        """
        Reset any internal state.
        """
        super().reset()


class DumbRandomAgent(AgentBaseDumb):
    """
        Randomly decided from non-visibility informed actions
    """
    
    def __init__(self, agent_id, assigned_sensors, assigned_satellites, do_nothing_rate=0.8):
        """
        Initialize the DumbRandomAgent.

        Parameters:
        - agent_id (int): Unique identifier for the agent.
        - assigned_sensors (list): List of sensors this agent can operate.
        - assigned_satellites (list): List of satellites this agent can control.
        - do_nothing_rate (float): Probability of choosing to do nothing (between 0 and 1).
        """
        super().__init__(agent_id, assigned_sensors, assigned_satellites)
        self.do_nothing_rate = do_nothing_rate
        self.is_rl_agent = False

    def decide(self, *args, **kwargs):
        """
        Decide on an action based on the do-nothing probability.

        Returns:
        - An action, either `None` (do nothing) or a (sensor, satellite) tuple.
        """
        if random.random() < self.do_nothing_rate:
            return super().do_nothing()
        return super().act_randomly()

    def reset(self):
        """
        Reset any internal state.
        """
        super().reset()


class RandomAgent(AgentBaseSmarter):
    """
        Randomly selects actions from visibility-informed actions
    """
    
    def __init__(self, agent_id, assigned_sensors, assigned_satellites, do_nothing_rate=0.8):
        """
        Initialize the RandomAgent.

        Parameters:
        - agent_id (int): Unique identifier for the agent.
        - assigned_sensors (list): List of sensors this agent can operate.
        - assigned_satellites (list): List of satellites this agent can control.
        - do_nothing_rate (float): Probability of choosing to do nothing (between 0 and 1).
        """
        super().__init__(agent_id, assigned_sensors, assigned_satellites)
        self.do_nothing_rate = do_nothing_rate
        self.is_rl_agent = False

    def decide(self, *args, **kwargs):
        """
        Decide on an action using the do-nothing rate and visibility-based action encoding.

        Returns:
        - An action, either a no-op or a visible (sensor, satellite) pair.
        """
        if random.random() < self.do_nothing_rate:
            return super().do_nothing()
        return super().act_randomly()

    def reset(self):
        """
        Reset any internal state.
        """
        super().reset()
