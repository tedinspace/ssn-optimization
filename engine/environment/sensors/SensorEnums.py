from enum import Enum

class GroundSensorModality(Enum):
    RADAR  = 1 # RADAR
    OPTICS = 2 # Optical Telescope
    
class SensorGeneralStatus(Enum):
    AVAILABLE  = "AVAILABLE" # (night for optics)
    NOT_AVAILABLE = "NOT_AVAILABLE" # (day for optics)