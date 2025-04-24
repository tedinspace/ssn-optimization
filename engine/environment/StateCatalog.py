
class StateCatalog: 
    def __init__(self, satellite_truth):
        self.current_catalog = {} # sat key to array of StateCatalogEntry
        self.satelitte_state_record = {} # sat key to single/latest StateCatalogEntry
        for sat_key in satellite_truth:
            self.current_catalog[sat_key]=StateCatalogEntry(satellite_truth[sat_key].orbit, 
                                                            satellite_truth[sat_key].orbit.epoch)
            self.satelitte_state_record[sat_key]=[]
            
        
    def update_state(self, sat_key, orbit, validity_time):   
        # TODO covariance
        self.satelitte_state_record[sat_key].append(self.current_catalog[sat_key])
        self.current_catalog[sat_key] = StateCatalogEntry(orbit, validity_time)
        
class StateCatalogEntry: 
    def __init__(self, orbit, last_seen, sigma_X_m=500, sigma_dX=0.1):
        self.orbit = orbit
        self.last_seen = last_seen
        self.sigma_X = sigma_X_m # [m] TODO - covariance standin 
        self.sigma_dX = sigma_dX # [m/s]