from engine.util.time import DEFAULT_DELTA_T, HPD, SPD
from astropy.time import Time

class Scenario:
    """
    A class to define a simulation scenario with a specified epoch, length, and time step.
    
    Properties:
        time_delta: Returns the time delta for the scenario in seconds.
        dt: Returns the time delta as a fraction of a day.
        scenario_length_hours: Returns the length of the scenario in hours.
        scenario_epoch: Returns the starting epoch of the scenario.
        scenario_end: Returns the ending epoch of the scenario.
        n_steps: Returns the number of time steps in the scenario.
    """
    
    def __init__(self, scenario_epoch, scenario_length, delta_t=None):
        """
        Initializes the Scenario class with a given epoch, length, and optional time delta.

        Args:
            scenario_epoch (astropy.time.Time): The start time of the simulation as an Astropy `Time` object.
            scenario_length (float): The length of the simulation in hours.
            delta_t (float, optional): The time step for the simulation in seconds. If not provided, uses `DEFAULT_DELTA_T`.
        """
        if delta_t is None:
            self._time_delta = DEFAULT_DELTA_T  # [s]
        else:
            self._time_delta = delta_t  # [s]

        self._dt = self._time_delta / SPD  # [fraction of day]

        self._scenario_length_hours = scenario_length  # [hours]

        self._scenario_epoch = scenario_epoch  # astropy.time.Time

        self._scenario_end = Time(scenario_epoch.mjd + scenario_length / HPD, format='mjd')

        self._n_steps = round(self._scenario_length_hours * 60 * (60 / self._time_delta))

    @property
    def time_delta(self):
        """
        Gets the time delta for the scenario.

        Returns:
            float: Time step for the simulation in seconds.
        """
        return self._time_delta

    @property
    def dt(self):
        """
        Gets the time delta as a fraction of a day.

        Returns:
            float: The time delta as a fraction of a day.
        """
        return self._dt

    @property
    def scenario_length_hours(self):
        """
        Gets the length of the scenario in hours.

        Returns:
            float: The length of the simulation scenario in hours.
        """
        return self._scenario_length_hours

    @property
    def scenario_epoch(self):
        """
        Gets the start epoch of the scenario.

        Returns:
            astropy.time.Time: The starting time of the simulation as an Astropy `Time` object.
        """
        return self._scenario_epoch

    @property
    def scenario_end(self):
        """
        Gets the end epoch of the scenario.

        Returns:
            astropy.time.Time: The end time of the simulation as an Astropy `Time` object.
        """
        return self._scenario_end

    @property
    def n_steps(self):
        """
        Gets the number of steps in the simulation.

        Returns:
            int: The number of time steps in the simulation.
        """
        return self._n_steps
