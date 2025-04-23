import random
from astropy import units

class Operations:
    
    def __init__(self, parent_sensor):
        self.parent_sensor = parent_sensor
        self.active_task = None
        self.scheduled_tasks = []
        self.schedule_ahead_limit_s = 60*60*units.s
               
    def sensing_logic(self, time, active_satellite_truth):
        '''
            future work to consider: 
            - if unable to acquire drop immediately and shift schedule forwards?
            - differentiate between maneuver during the first/last half of the interval
            - more complex acquisition model? 
            
        '''
        if not self.active_task.tasking_started:
            self.active_task.tasking_started = True
             
            if not self.parent_sensor.has_line_of_sight(active_satellite_truth.orbit, time):
                # CASE 1: UNABLE TO ACQUIRE
                self.active_task.able_to_acquire = False
                print("[ALERT] UNABLE TO ACQUIRE")
                print(self.active_task.task_request.sensor_key)
                print(self.active_task.task_request.sat_key)
            else:
                # CASE 2: ABLE TO ACQUIRE
                self.active_task.able_to_acquire = True
                # Question 1: has it maneuver since the state (that the sensor has) was updated
                maneuvers_to_estimate = []
                for past_maneuver in active_satellite_truth.maneuvers_occurred:
                    if past_maneuver.time > self.active_task.task_request.available_state.last_seen:
                        maneuvers_to_estimate.append(past_maneuver) 
                #print(len(maneuvers_to_estimate))
                # Question 2: will it maneuver during the sensing duration? 
                
                maneuvers_to_estimate_while_tasking = []
                for future_maneuver in active_satellite_truth.maneuvers_remaining:
                    if future_maneuver.time > self.active_task.scheduled_start and future_maneuver.time < self.active_task.scheduled_end:
                        print("[ALERT] OCCURS DURING THE TASKING")
                        maneuvers_to_estimate_while_tasking.append(future_maneuver)
                #print(len(maneuvers_to_estimate_while_tasking))        
                if len(maneuvers_to_estimate)> 0 or len(maneuvers_to_estimate_while_tasking)>0:
                    # note maneuvers were detected 
                    self.active_task.maneuvers_detected = True
                
                
            # Question 3: what will happen to the state estimation (if maneuvered, maneuvering, or not)
    
    def tick(self, time, incoming_valid_task_messages, satellite_truth_map):
        completed_task = None
        if self.active_task:
            
            if time > self.active_task.scheduled_start and time < self.active_task.scheduled_end  :
                # tasking
                self.sensing_logic(time, satellite_truth_map[self.active_task.task_request.sat_key])

            if time > self.active_task.scheduled_end :
                # end of tasking
                self.active_task.tasking_completed = True
                completed_task = self.active_task
                self.active_task = None
                
        
        # 1. promote active task
        if self.active_task == None:
            # no active task
            if len(self.scheduled_tasks) > 0:
                # i. take next scheduled (if any)
                self.active_task = self.scheduled_tasks.pop(0)                

            elif len(incoming_valid_task_messages) > 0:
                # ii. take next incoming (if any)
                
                self.active_task = TaskRecord(randomize_slew_time(time), incoming_valid_task_messages.pop(0))
        # 2. schedule remaining tasks
        unschedulable_task_request = []    
        for task_req in incoming_valid_task_messages:
            if len(self.scheduled_tasks) ==0:
                # A. nothing on the queue
                requestedStartTime =  randomize_slew_time(time) 
                
                
                if self.active_task.task_request.sat_key != task_req.sat_key: # TODO available at request time
                    # not the active task AND TODO valid time
                    
                    self.scheduled_tasks.append(TaskRecord(requestedStartTime, task_req))
                else: 
                    unschedulable_task_request.append(task_req)
            else:
                # B. stuff already scheduled 
                requestedStartTime =  randomize_slew_time(self.scheduled_tasks[-1].scheduled_end ) 
               
                if (requestedStartTime < time + self.schedule_ahead_limit_s 
                    and self.scheduled_tasks[-1].task_request.sat_key != task_req.sat_key):
                                 
                    # not past time limit + not the same as just looked at + 
                    self.scheduled_tasks.append( TaskRecord(requestedStartTime, task_req))
                else: 
                    unschedulable_task_request.append(task_req)
                    
        return unschedulable_task_request, completed_task

                
        
        
            

class TaskRecord:
    def __init__(self,start_time, task_request):
        '''
            task_request - PendingTaskMessage
        '''
        self.task_request = task_request
        self.task_length_mins =  random.uniform(3.5, 7.5) # [mins]
        self.scheduled_start = start_time
        self.scheduled_end = start_time + self.task_length_mins * 60 * units.s  
        self.tasking_started = False
        self.tasking_completed = False
        self.able_to_acquire = None
        self.maneuvers_detected = False
        
        
        
# -----------------------------------------------------------------------------------------
#                                          FUNCTIONS
# -----------------------------------------------------------------------------------------
def randomize_slew_time(base_time):
    '''base_time (astropy.time.Time)'''
    return base_time +  random.uniform(1.5, 3.5) * 60 * units.s  



