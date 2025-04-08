from engine.environment.sensors.SensorEnums import GroundSensorModality
from engine.environment.sensors.SensorInfo import SensorInfo
from engine.environment.sensors.GroundSensor import GroundSensor

'''NOTE: these locations may be inaccurate; they are for testing purposes'''

def mhr():
    '''https://www.haystack.mit.edu/the-millstone-hill-geospace-facility'''
    return SensorInfo('mhr', [42.61762, -71.49038, 0], GroundSensorModality.RADAR)

def ascension():
    return SensorInfo('ascension', [-7.678805483927795, -13.265374101627982,0], GroundSensorModality.RADAR)

def holt():
    return SensorInfo('holt', [-22.2873117,115.070292, 0], GroundSensorModality.RADAR)

def sst():
    '''https://en.wikipedia.org/wiki/Space_Surveillance_Telescope'''
    return SensorInfo('sst', [-22.2873117,115.070292, 0], GroundSensorModality.OPTICS)

def maui():
    return SensorInfo('maui',  [20.708259458876853, -156.2567944944128, 0], GroundSensorModality.OPTICS)

def socorro():
    return SensorInfo('socorro', [32.82, -106.66, 0], GroundSensorModality.OPTICS)

def ssn():
    return {
        'mhr': mhr(), 
        'ascension': ascension(), 
        'holt': holt(), 
        'sst': sst(), 
        'maui': maui(), 
        'socorro': socorro() 
    }
    
def load_sensor_map(sensor_keys, scenario_configs):
    SSN = ssn()
    sensor_map = {}
    for skey in sensor_keys:
        sensor_info = SSN[skey]
        sensor_map[skey]=GroundSensor(sensor_info.name, sensor_info.lla, sensor_info.modality, scenario_configs)
        
    return sensor_map