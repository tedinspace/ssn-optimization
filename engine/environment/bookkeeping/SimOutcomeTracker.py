import pickle
from engine.environment.bookkeeping.EventTracker import Event
from engine.environment.sensors.Communication import SensorResponse
class SimOutcomeTracker:
    def __init__(self, id, sensor_keys, sat_keys, n_rounds):
        self.id = id
        self.sensor_keys = sensor_keys
        self.sat_keys = sat_keys
        self.n_rounds = n_rounds
        
        # metrics 
        self.rewards = []
        self.uncertainty_static = []
        self.uncertainty_prop = []
        self.unique_mans = []
        self.unique_obj = []
        self.unique_mans_in_scenario = []
        self.tasks_issued = []
        self.state_updates =[]
        self.state_updates_nom = []
        self.state_updates_man = []
        self.lost_objects = []
        
        self.dropped_offline = []
        self.dropped_scheduling =[]
        self.dropped_scheduling_2 = []
        self.dropped_track_failure = []
        
    def save_instance(self, file_with_path):
        '''pickle tracker to study results'''
        with open(file_with_path, "wb") as f:
            pickle.dump(self, f)
        
    def log_round(self, env, state_cat, total_reward):
        # 1. reward
        self.rewards.append(total_reward)
        # 2. 1. covariance of catalog (prop/unprop)
        un_prop, prop = env.tracker.comp_saved_cat_uncertainty(state_cat)
        self.uncertainty_static.append(un_prop)
        self.uncertainty_prop.append(prop)        
        # 3. unique objects and maneuvers
        self.unique_mans.append(len(env.tracker.unique_mans))
        self.unique_obj.append(len(env.tracker.unique_sats))
        self.unique_mans_in_scenario.append(env.unique_maneuvers)
        
        # 4. total tasks issued
        self.tasks_issued.append(env.tracker.pull_record(Event.TASKING_ISSUED))
        
        # 5. total state updates
        self.state_updates.append(env.tracker.pull_record(Event.STATE_UPDATE))
        self.state_updates_nom.append(env.tracker.pull_record(SensorResponse.CATALOG_STATE_UPDATE_NOMINAL))
        self.state_updates_man.append(env.tracker.pull_record(SensorResponse.CATALOG_STATE_UPDATE_MANEUVER))
        
        # 6. lost 
        self.lost_objects.append(len(env.tracker.lost_objects))
        
        # 7. dropped 
        self.dropped_offline.append(env.tracker.pull_record(SensorResponse.DROPPED_SENSOR_OFFLINE))
        self.dropped_scheduling.append(env.tracker.pull_record(SensorResponse.DROPPED_SCHEDULING))
        self.dropped_scheduling_2.append(env.tracker.pull_record(SensorResponse.DROPPED_NOT_VISIBLE))
        self.dropped_track_failure.append(env.tracker.pull_record(SensorResponse.FAILURE_OBJECT_LOST))