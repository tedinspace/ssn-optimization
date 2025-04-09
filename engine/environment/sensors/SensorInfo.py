class SensorInfo:
    """
    A class to represent a sensor's basic information.

    Attributes:
        name (str): The name of the sensor.
        lla (list): length 3 list representing the sensor's location in latitude, longitude, and altitude (LLA).
        modality (engine.environment.sensors.GroundSensor.GroundSensorModality): The modality or type of sensor 

    Methods:
        __init__(self, name, lla, modality):
            Initializes a new instance of the SensorInfo class.
    """

    def __init__(self, name, lla, modality):
        """
        Initializes a new instance of the SensorInfo class.

        Args:
            name (str): The name of the sensor.
            lla (tuple): A tuple representing the sensor's location in latitude, longitude, and altitude.
            modality (engine.environment.sensors.GroundSensor.GroundSensorModality): The modality or type of sensor 
        """
        self.name = name
        self.lla = lla
        self.modality = modality
