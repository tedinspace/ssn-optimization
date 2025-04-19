

class Operations:
    
    def __init__(self, mode):
        self.mode = mode 
        self.active_task = None
        self.scheduled_tasks = []
        
        
    def is_available(self):
        return self.active_task !=None
    
    def tick(self, time, incoming_valid_task_messages):
        if self.active_task:
            x = 1
    

class ActiveTask:
    def __init__(self, task_request):
        '''
            task_request - PendingTaskMessage
        '''
        self.task_request = task_request
         