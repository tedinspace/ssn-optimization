import random
from astropy import units

class Operations:
    
    def __init__(self, mode):
        self.mode = mode 
        self.active_task = None
        self.scheduled_tasks = []
        self.schedule_ahead_limit_s = 60*60*units.s
        
           
    def is_available(self):
        return self.active_task !=None
    
    def tick(self, time, incoming_valid_task_messages, satellite_truth_map):
        completed_task = None
        if self.active_task:
            
            # if self.active_task.scheduled_start > time: 
            #     print(time)
            #     print(self.active_task.scheduled_start)
            #     print(self.active_task.task_request.sensor_key)
            #     print('slewing to')
            #     print(self.active_task.task_request.sat_key)
            #     print(satellite_truth_map[self.active_task.task_request.sat_key])
        
            if time > self.active_task.scheduled_start and time < self.active_task.scheduled_end  :
                self.active_task.tasking_started = True
                #print(self.active_task.task_request.sensor_key)
                #print('looking looking at')
                #print(self.active_task.task_request.sat_key)
            #else:
            #    print('much ado')
            if time > self.active_task.scheduled_end :
                #print('---')
                #print(time)
                #print(self.active_task.scheduled_start)
                #print(self.active_task.task_length_mins)
                #print(self.active_task.scheduled_end)
                #print(self.active_task.task_request.sensor_key)
                #print('done looking at')
                #print(self.active_task.task_request.sat_key)
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
        
        
        
# -----------------------------------------------------------------------------------------
#                                          FUNCTIONS
# -----------------------------------------------------------------------------------------
def randomize_slew_time(base_time):
    '''base_time (astropy.time.Time)'''
    return base_time +  random.uniform(1.5, 3.5) * 60 * units.s  

