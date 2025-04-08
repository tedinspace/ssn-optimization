from enum import Enum

class GroundSensorModality(Enum):
    """
    Enum representing different modalities of ground sensors.

    Attributes:
        RADAR (int): Represents a RADAR sensor.
        OPTICS (int): Represents an Optical Telescope sensor.
    """
    RADAR = 1  # RADAR
    OPTICS = 2  # Optical Telescope

class SensorGeneralStatus(Enum):
    """
    Enum representing the general status of a sensor.

    Attributes:
        AVAILABLE (str): Indicates that the sensor is available (e.g., night for optics).
        NOT_AVAILABLE (str): Indicates that the sensor is not available (e.g., day for optics).
    """
    AVAILABLE = "AVAILABLE"  # (night for optics)
    NOT_AVAILABLE = "NOT_AVAILABLE"  # (day for optics)
