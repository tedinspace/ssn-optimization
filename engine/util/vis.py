
from astropy.coordinates import CartesianRepresentation, GCRS, AltAz
from astropy import units 
from engine.util.astro import create_earth_location, tle_to_orbit
from engine.environment.Scenario import Scenario
from engine.builder.sensors.ssn import ssn
from engine.builder.satellites.states import TLE_LIBRARY


def generate_vis_map(sensor_keys, sat_keys, scenario_configs=Scenario()):
    SSN = ssn()

    sensor_map = {}
    vis_map = {}
    for skey in sensor_keys:
        sensor_map[skey]= create_earth_location(SSN[skey].lla)
        vis_map[skey]=set()
        
    sat_map = {}
    vis_map_sat = {}
    for skey in sat_keys:
        sat_map[skey]=tle_to_orbit(TLE_LIBRARY[skey][1], TLE_LIBRARY[skey][2], scenario_configs.scenario_epoch)
        vis_map_sat[skey]=set()
        
    time = scenario_configs.scenario_epoch.copy()
    dt = 30*3600*units.s
    while time < scenario_configs.scenario_end:
        for sensor in sensor_map:
            az_el = AltAz(obstime=time, location=sensor_map[sensor])
            for sat in sat_map:
                orbit = sat_map[sat].propagate(time)
                if not sat in  vis_map[sensor]:
                    ##
                    if  GCRS( CartesianRepresentation(orbit.r << units.km), obstime=orbit.epoch).transform_to(az_el).alt > 5*units.deg:
                        vis_map[sensor].add(sat)
                        vis_map_sat[sat].add(sensor)
                    
        time += dt
        
    return vis_map, vis_map_sat


def vis_map_to_action_tuples(vis_map):
    action_tuples = [None]
    for sensor in vis_map:
        for sat in vis_map[sensor]:
            action_tuples.append((sensor,sat))
            
    return action_tuples
    