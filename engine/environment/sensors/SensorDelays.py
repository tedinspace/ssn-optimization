import random
from astropy import units 

class SensorDelays:
    def __init__(self):
        self.task_message_delivery_delay_base = 7.5 # [mins] agent --> (delay+-random) --> sensor
        self.task_message_delivery_delay_rand = [-2.5,2.5] # [-mins, +mins] randomness added tasking delay 
        
    def message_delivery_time(self, time):
        return time + (self.task_message_delivery_delay_base + random.uniform(self.task_message_delivery_delay_rand[0], self.task_message_delivery_delay_rand[1]) )*60*units.s, 