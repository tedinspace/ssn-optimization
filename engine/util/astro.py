from sgp4.api import Satrec
from astropy import units as u
from astropy.coordinates import CartesianRepresentation, TEME, GCRS
from astropy.time import Time
from astropy.units.quantity import Quantity
from poliastro.twobody import Orbit
from poliastro.bodies import Earth
    


def tle_to_orbit(line1, line2, epoch=None):
    '''given a TLE there are a number of steps '''
    
    # TLE --> SATREC
    satellite = Satrec.twoline2rv(line1, line2)

    # unpack epoch if not provided
    if epoch == None:
        epoch = Time(satellite.jdsatepoch + satellite.jdsatepochF, format='jd')
    
    # SATREC --> TEME RV
    _, r_teme, v_teme = satellite.sgp4(epoch.jd1, epoch.jd2) # TEME

    # TEME --> GCRS
    r_c_gcrs = (TEME( CartesianRepresentation(r_teme << u.km), obstime=epoch).transform_to(GCRS(obstime=epoch)).cartesian)
    v_c_gcrs = (TEME( CartesianRepresentation(v_teme << u.km / u.s), obstime=epoch).transform_to(GCRS(obstime=epoch)).cartesian)
    r_gcrs = Quantity([r_c_gcrs.x.value, r_c_gcrs.y.value, r_c_gcrs.z.value], unit =u.km)
    v_gcrs = Quantity([v_c_gcrs.x.value, v_c_gcrs.y.value, v_c_gcrs.z.value], unit =u.km/u.s)

    # GCRS --> ORBIT
    return Orbit.from_vectors(Earth, r_gcrs, v_gcrs, epoch)
