from enum import Enum
from astropy.coordinates import AltAz,CartesianRepresentation, GCRS, SkyCoord, get_sun
from astropy import units 
from engine.util.astro import create_earth_location
from engine.environment.sensors.Communication import CommunicationPipeline, SensorResponse
from engine.environment.sensors.SensorLogic import Operations

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
        ONLINE (str): Indicates that the sensor is available (e.g., night for optics).
        OFFLINE (str): Indicates that the sensor is not available (e.g., day for optics).
    """
    ONLINE = "ONLINE"  # (night for optics)
    OFFLINE = "OFFLINE"  # (day for optics)


class GroundSensor: 
    def __init__(self,name, lla, mode=GroundSensorModality.RADAR, scenario=None):
        '''scenario required for optics'''
        self.name = name
        self.sensor_key = name
        self.mode = mode
               
        self.general_status = SensorGeneralStatus.ONLINE 
        self.availability_trans_times = []
        self.availability_trans_to_status = []
        
        self.location = create_earth_location(lla)
        
        self.elevation_threshold = 4.5 * units.deg
        self.night_threshold = -12 *units.deg # astro twilight
        if self.mode == GroundSensorModality.OPTICS:
            self._init_optics(scenario.scenario_epoch, scenario.scenario_end)
            
        self.operator = Operations(self)
            
        # --------------TASKING LOGIC --------------
        self.pipeline = CommunicationPipeline(self.sensor_key)

    def _get_azel(self, time):
        '''time - astropy.time.Time '''
        return AltAz(obstime=time, location=self.location)
    
    def _sun_at_sensor(self, time):
        sun = get_sun(time)
        return  SkyCoord(ra=sun.ra, dec=sun.dec).transform_to(self._get_azel(time))
    def _is_night(self,time):
        '''is it night at sensor given time - astropy.time.Time '''
        return self._sun_at_sensor(time).alt < self.night_threshold
    
    def _init_optics(self,start_time,end_time, rate=5*60*units.s):
        '''
        start_time - astropy.time.Time
        end_time - astropy.time.Time
        rate - rate + accuracy 
        '''
        self.general_status = SensorGeneralStatus.ONLINE if self._is_night(start_time) else SensorGeneralStatus.OFFLINE

        day_night_transition_times = []
        day_night_transition_status = []
        
        prev_status = self.general_status
        current_time = start_time.copy()+rate # move ahead one timestep
        
        while current_time < end_time:
            curr_status = SensorGeneralStatus.ONLINE if self._is_night(current_time) else SensorGeneralStatus.OFFLINE
            if curr_status!=prev_status:
                day_night_transition_status.append(curr_status) # becomes this status
                # conservative time cutoffs 
                if current_time == SensorGeneralStatus.OFFLINE:
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
                
                # if we are going offline
                if self.general_status == SensorGeneralStatus.OFFLINE:
                    print('off')
                    print(self.operator.active_task)
                    print(len(self.operator.scheduled_tasks))
                    # > drop active task
                    if self.operator.active_task !=None:
                        self.pipeline.drop_message(SensorResponse.DROPPED_SCHEDULING, self.operator.active_task.task_request, time)
                        self.operator.active_task = None
                    # > drop scheduled tasks
                    if len(self.operator.scheduled_tasks)!=0:
                   
                        for task in self.operator.scheduled_tasks:
                            self.pipeline.drop_message(SensorResponse.DROPPED_SCHEDULING, task.task_request, time)
                        
                        self.operator.scheduled_tasks = []
                else:
                    print('on')
                    print(self.operator.active_task)
                    print(len(self.operator.scheduled_tasks))
                        
                    
     
    def has_line_of_sight(self, orbit, time):
        ''' 
        orbit - poliastro.twobody.Orbit
        time - astropy.time.Time
        '''
        if orbit.epoch.mjd != time.mjd:
            orbit = orbit.propagate(time)
        #print(SkyCoord(ra=radec.ra, dec=radec.dec).transform_to(altaz_frame).alt)
        #return orbit_to_sky_coord(orbit).transform_to(self._get_azel(time)).alt > self.elevation_threshold
        return   GCRS( CartesianRepresentation(orbit.r << units.km), obstime=orbit.epoch).transform_to(self._get_azel(time)).alt > self.elevation_threshold
        
        
                
    def pass_to_pipeine(self, time, agent_id, sat_key, frozen_state):
        '''
            time - astropy.time.Time
            agent_id - unique string
            sat_key - unique string
            frozen_state - StateCatalogEntry
        '''
        self.pipeline.receive_task_request( time, agent_id, sat_key, frozen_state)
         
    
    def tick(self, time, satellite_truth_map):

        '''advance sensor in time - astropy.time.Time'''
        self._update_availability(time) # check for status changes
                
        task_messages_unvetted = self.pipeline.check_for_incoming_tasks(time)
        
        # vet task messages
        if self.general_status == SensorGeneralStatus.ONLINE:
            # sensor online
            task_messages_vetted = []
            task_messages_rejected = []
            for message in task_messages_unvetted:
                if self.has_line_of_sight(message.available_state.orbit, time)and self.has_line_of_sight(message.available_state.orbit, time+self.operator.schedule_ahead_limit_s):
                    task_messages_vetted.append(message)
                else:
                    task_messages_rejected.append(message)
            # reject for visibility
            self.pipeline.drop_messages(SensorResponse.DROPPED_NOT_VISIBLE, task_messages_unvetted, time)
            
            # TODO try to schedule vetted messages
            # TODO no scheduling if sensor is scheduled to be offline 
            unschedulable_task_requests, completed_task = self.operator.tick(time,task_messages_vetted, satellite_truth_map )
            if unschedulable_task_requests:
                self.pipeline.drop_messages(SensorResponse.DROPPED_SCHEDULING, unschedulable_task_requests, time)
            if completed_task!=None:
                if completed_task.able_to_acquire == True:
                    self.pipeline.send_state_updated(completed_task, time)
                else:
                    self.pipeline.drop_message(SensorResponse.FAILURE_OBJECT_LOST, completed_task.task_request, time)             
                
        else:
            # sensor offline; 
            self.pipeline.drop_messages(SensorResponse.DROPPED_SENSOR_OFFLINE, task_messages_unvetted, time)
                
    
    def check_pipeline(self, time):
        return self.pipeline.check_for_outgoing_messages(time) 


