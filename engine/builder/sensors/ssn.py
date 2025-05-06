from engine.environment.sensors.SensorInfo import SensorInfo
from engine.environment.sensors.GroundSensor import GroundSensor, GroundSensorModality

'''NOTE: These locations may be inaccurate; they are for testing purposes.'''

def mhr():
    '''
    Returns a SensorInfo object for the Millstone Hill Geospace Facility (MHR).
    
    Reference:
    - Location: Millstone Hill, MIT (https://www.haystack.mit.edu/the-millstone-hill-geospace-facility)
    - Modality: Radar
    '''
    return SensorInfo('mhr', [42.61762, -71.49038, 0], GroundSensorModality.RADAR)

def boston():

    return SensorInfo('boston', [42.61762, -71.49038, 0], GroundSensorModality.RADAR)

def ascension():
    '''
    Returns a SensorInfo object for the Ascension sensor location.
    
    - Modality: Radar
    '''
    return SensorInfo('ascension', [-7.678805483927795, -13.265374101627982, 0], GroundSensorModality.RADAR)

def holt():
    '''
    Returns a SensorInfo object for the Holt sensor location.
    
    - Modality: Radar
    '''
    return SensorInfo('holt', [-22.2873117, 115.070292, 0], GroundSensorModality.RADAR)

def sst():
    '''
    Returns a SensorInfo object for the Space Surveillance Telescope (SST).
    
    Reference:
    - Location: Space Surveillance Telescope, Australia (https://en.wikipedia.org/wiki/Space_Surveillance_Telescope)
    - Modality: Optics
    '''
    return SensorInfo('sst', [-22.2873117, 115.070292, 0], GroundSensorModality.OPTICS)

def maui():
    '''
    Returns a SensorInfo object for the Maui sensor location.
    
    - Modality: Optics
    '''
    return SensorInfo('maui', [20.708259458876853, -156.2567944944128, 0], GroundSensorModality.OPTICS)

def socorro():
    '''
    Returns a SensorInfo object for the Socorro sensor location.
    
    - Modality: Optics
    '''
    return SensorInfo('socorro', [32.82, -106.66, 0], GroundSensorModality.OPTICS)

def vandenberg():
    # 34.7420° N, 120.5724° W
    return SensorInfo('vandenberg',[34.7420, -120.5724, 0 ], GroundSensorModality.RADAR )

def ssn():
    '''
    Returns a dictionary containing SensorInfo objects for various sensor locations.

    Keys:
        - 'mhr': Millstone Hill Geospace Facility (Radar)
        - 'ascension': Ascension (Radar)
        - 'holt': Holt (Radar)
        - 'sst': Space Surveillance Telescope (Optics)
        - 'maui': Maui (Optics)
        - 'socorro': Socorro (Optics)
    '''
    return {
        'mhr': mhr(), 
        'boston': boston(), # mhr clone 
        'ascension': ascension(), 
        'holt': holt(), 
        'sst': sst(), 
        'maui': maui(), 
        'socorro': socorro(),
        'vandenberg': vandenberg()
    }

def load_sensor_map(sensor_keys, scenario_configs):
    '''
    Loads and returns a mapping of sensor keys to corresponding GroundSensor objects.

    Parameters:
        - sensor_keys (list): A list of sensor names (e.g., ['mhr', 'ascension', 'holt', ...])
        - scenario_configs (dict): Configuration dictionary for the scenario, which will be used to initialize each GroundSensor.

    Returns:
        - sensor_map (dict): A dictionary where keys are sensor names and values are GroundSensor objects.
    '''
    SSN = ssn()
    sensor_map = {}
    for skey in sensor_keys:
        sensor_info = SSN[skey]
        sensor_map[skey] = GroundSensor(sensor_info.name, sensor_info.lla, sensor_info.modality, scenario_configs)
        
    return sensor_map
