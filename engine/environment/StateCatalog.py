
class StateCatalog: 
    def __init__(self, satellite_truth):
        self.current_catalog = {} # [sat_key]:StateCatalogEntry
        for sat_key in satellite_truth:
            self.current_catalog[sat_key]=StateCatalogEntry(satellite_truth[sat_key].orbit, satellite_truth[sat_key].orbit.epoch)
            
        
    def update_state(self, sat_key, record):   
        self.current_catalog[sat_key] = StateCatalogEntry(record.orbit, record.orbit_validity_time, record.sigma_X, record.sigma_dX)
        
class StateCatalogEntry: 
    def __init__(self, orbit, last_seen, sigma_X_m=500, sigma_dX=0.1):
        self.orbit = orbit
        self.last_seen = last_seen
        self.sigma_X = sigma_X_m # [m] - covariance standin 
        self.sigma_dX = sigma_dX # [m/s] - covariance standin 