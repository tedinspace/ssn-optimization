from astropy.coordinates import EarthLocation, AltAz, SkyCoord, get_sun
from astropy import units 

from enum import Enum

class SensorModality(Enum):
    RADAR  = 1 # RADAR
    OPTICS = 2 # Optical Telescope

class SensorGeneralStatus(Enum):
    AVAILABLE  = "AVAILABLE" # (night for optics)
    NOT_AVAILABLE = "NOT_AVAILABLE" # (day for optics)

class GroundSensor: 
    def __init__(self, lla, mode=SensorModality.RADAR, scenario=None):
        '''scenario required for optics'''
        self.mode = mode
        
            
        self.general_status = SensorGeneralStatus.AVAILABLE 
        self.availability_trans_times = []
        self.availability_trans_to_status = []
        
        self.location = EarthLocation.from_geodetic(lla[1], lla[0], lla[2]) # (lon,lat,alt)
        
        
        self.night_threshold = -12 *units.deg # astro twilight
        if self.mode == SensorModality.OPTICS:
            self._init_optics(scenario.scenario_epoch, scenario.scenario_end)

    def _get_azel(self, time):
        '''time - astropy.time.Time '''
        return AltAz(obstime=time, location=self.location)
    
    def _sun_at_sensor(self, time):
        altaz_frame = self._get_azel(time)
        sun = get_sun(time)
        return  SkyCoord(ra=sun.ra, dec=sun.dec).transform_to(altaz_frame)
    def _is_night(self,time):
        '''is it night at sensor given time - astropy.time.Time '''
        return self._sun_at_sensor(time).alt < self.night_threshold
    
    def _init_optics(self,start_time,end_time, rate=5*60*units.s):
        '''
        start_time - astropy.time.Time
        end_time - astropy.time.Time
        rate - rate + accuracy 
        '''
        self.general_status = SensorGeneralStatus.AVAILABLE if self._is_night(start_time) else SensorGeneralStatus.NOT_AVAILABLE

        day_night_transition_times = []
        day_night_transition_status = []
        
        prev_status = self.general_status
        current_time = start_time.copy()+rate # move ahead one timestep
        
        while current_time < end_time:
            curr_status = SensorGeneralStatus.AVAILABLE if self._is_night(current_time) else SensorGeneralStatus.NOT_AVAILABLE
            if curr_status!=prev_status:
                day_night_transition_status.append(curr_status) # becomes this status
                # conservative time cutoffs 
                if current_time == SensorGeneralStatus.NOT_AVAILABLE:
                    day_night_transition_times.append(current_time-rate) 
                else:
                    day_night_transition_times.append(current_time)
                prev_status = curr_status
    
            current_time+=rate
            
        self.availability_trans_times = day_night_transition_times
        self.availability_trans_to_status = day_night_transition_status
     
    def _update_availability(self, time):
        '''time - astropy.time.Time'''    
        if self.availability_trans_times:
            # at some point availability status will change
            
            if time >= self.availability_trans_times[0]:        
                self.general_status = self.availability_trans_to_status[0] 
                # remove from transition array
                self.availability_trans_times = self.availability_trans_times[1:]
                self.availability_trans_to_status = self.availability_trans_to_status[1:]
     
    def tick(self, time):
        '''advance sensor in time - astropy.time.Time'''
        self._update_availability(time) # check for status changes
        #if self.general_status == SensorGeneralStatus.AVAILABLE:

        
        