import random
import numpy as np
from astropy.time import Time
from astropy import units
from poliastro.maneuver import Maneuver
from engine.util.time import HPD
from engine.util.astro import tle_to_orbit

class SatelliteTruth:
    def __init__(self, name, l1, l2, scenario_configs, reepoch_hours=None):
        """
        Initializes the SatelliteTruth object with the provided parameters.
        
        Args:
            name (str): The name of the satellite.
            l1 (str): TLE line 1 for the satellite.
            l2 (str): TLE line 2 for the satellite.
            scenario_configs (object): Scenario configuration object containing simulation parameters.
            reepoch_hours (float, optional): If provided, this indicates the number of hours to reepoch the satellite's orbit.
        
        Attributes:
            name (str): The name of the satellite.
            l1 (str): TLE line 1.
            l2 (str): TLE line 2.
            scenario_epoch (astropy.time.Time): The epoch time of the scenario.
            is_reepoched (bool): Flag indicating whether the satellite has been reepoch'd.
            reepoch_hours (float or None): The number of hours to reepoch the satellite's orbit.
            reepoch (astropy.time.Time or None): The reepoch time if reepoch_hours is provided.
            orbit (Orbit): The satellite's orbital state, initialized from TLE lines.
            n_maneuvers (int): The number of maneuvers the satellite will undergo.
            maneuvers (list): List of maneuvers that the satellite will perform.
            maneuvers_occurred (list): List of maneuvers that have already occurred.
            maneuvers_remaining (list): List of maneuvers that are yet to occur.
        """
        self.name = name
        self.l1 = l1
        self.l2 = l2
        
        # Time related initialization
        self.scenario_epoch = scenario_configs.scenario_epoch
        self.is_reepoched = False
        self.reepoch_hours = None
        self.reepoch = None
        if reepoch_hours != None:
            self.is_reepoched = True
            self.reepoch_hours = reepoch_hours
            self.reepoch = Time(self.scenario_epoch.mjd - reepoch_hours/HPD, format='mjd')

        # Initialize orbital state from TLE lines
        self.orbit = tle_to_orbit(l1, l2, self.reepoch)
        
        # Maneuver-related attributes
        self.n_maneuvers = 0
        self.maneuvers = []
        self.maneuvers_occurred = []
        self.maneuvers_remaining = []

    def add_maneuvers(self, maneuver_list):
        """
        Adds a list of maneuvers to the satellite and resets the list of occurred maneuvers.

        Args:
            maneuver_list (list): A list of Maneuver objects representing the maneuvers.
        
        Updates:
            maneuvers_occurred (list): Resets the list of maneuvers that have occurred.
            maneuvers_remaining (list): Sets the remaining maneuvers.
            maneuvers (list): Updates the maneuvers list.
            n_maneuvers (int): Updates the number of maneuvers.
        """
        maneuver_list = sorted(maneuver_list, key=lambda x: x.time)
        self.maneuvers_occurred = []
        self.maneuvers_remaining = maneuver_list
        self.maneuvers = maneuver_list
        self.n_maneuvers = len(maneuver_list)

    def maneuvered_between(self, last_epoch, time_now):
        """
        Checks if the satellite has undergone a maneuver between two specified times.

        Args:
            last_epoch (astropy.time.Time): The time of the previous state.
            time_now (astropy.time.Time): The current time to check for maneuvers.

        Returns:
            bool: True if the satellite has maneuvered between last_epoch and time_now, False otherwise.
        """
        didManuever = False
        for m in self.maneuvers:
            if m.time >= last_epoch and m.time <= time_now:
                return True
        return didManuever

    def tick(self, t):
        """
        Advances the satellite state to the given time, propagating the orbit and applying maneuvers if necessary.

        Args:
            t (astropy.time.core.Time): The current time to propagate the orbit to.
        
        Updates:
            maneuvers_remaining (list): Updates the remaining maneuvers.
            maneuvers_occurred (list): Adds any maneuvers that have occurred by the time t.
            orbit (Orbit): Updates the satellite's orbit, propagating it and applying any applicable maneuvers.
        """
        remaining = []
        for m in self.maneuvers_remaining:
            if m.time <= t:
                # If the maneuver time has passed, apply the maneuver and update the orbit
                m.occurred = True
                self.orbit = self.orbit.propagate(m.time).apply_maneuver(Maneuver.impulse(m.maneuver << (units.m / units.s)))
                self.maneuvers_occurred.append(m)
            else:
                remaining.append(m)
        self.maneuvers_remaining = remaining
        self.orbit = self.orbit.propagate(t)

# --------------------------------------------------------------------------------
#                                  MANEUVER CLASS                                 |
# --------------------------------------------------------------------------------
class ManeuverDetails:
    def __init__(self, magnitude_dv, hours_into_scenario, scenario_configs):
        """
        Initializes the ManeuverDetails object with the provided parameters.

        Args:
            magnitude_dv (float): The magnitude of the delta-v for the maneuver.
            hours_into_scenario (float): The number of hours into the scenario when the maneuver occurs.
            scenario_configs (object): Scenario configuration object containing simulation parameters.

        Attributes:
            dir (np.ndarray): A normalized direction vector for the maneuver.
            maneuver (np.ndarray): The delta-v vector for the maneuver, scaled by magnitude_dv.
            time (astropy.time.Time): The exact time the maneuver occurs.
            occurred (bool): Flag indicating if the maneuver has already occurred.
        """
        self.dir = np.array([random.random(), random.random(), random.random()])
        self.dir = self.dir / np.sum(self.dir)  # Normalize the direction vector
        self.maneuver = self.dir * magnitude_dv  # Scale the direction by magnitude_dv
        self.time = scenario_configs.scenario_epoch + hours_into_scenario * units.h  # Calculate the maneuver time
        self.occurred = False  # The maneuver has not yet occurred