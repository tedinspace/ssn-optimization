from sgp4.api import Satrec
from astropy import units as u
from astropy.coordinates import CartesianRepresentation, TEME, GCRS, SkyCoord, EarthLocation
from astropy.time import Time
from astropy.units.quantity import Quantity
from poliastro.twobody import Orbit
from poliastro.bodies import Earth

def tle_to_orbit(line1, line2, epoch=None):
    '''
    Converts a TLE (Two-Line Element set) into an orbit object using the SGP4 model and transforms it 
    into the GCRS frame.

    Parameters:
        - line1 (str): The first line of the TLE.
        - line2 (str): The second line of the TLE.
        - epoch (astropy.time.Time, optional): The time of the TLE epoch. If None, the epoch from the TLE is used.

    Returns:
        - Orbit: A poliastro Orbit object in the GCRS frame.

    '''
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

def orbit_to_sky_coord(orbit):
    '''
    Converts a poliastro Orbit object to an Astropy SkyCoord object, which represents the 
    position in the GCRS frame in a more convenient format for astronomical calculations.

    Parameters:
        - orbit (poliastro.twobody.Orbit): A poliastro Orbit object.

    Returns:
        - SkyCoord: An Astropy SkyCoord object representing the position of the orbit in the GCRS frame.

    '''
    return SkyCoord(x=orbit.r[0], y=orbit.r[1], z=orbit.r[2], unit=u.km, representation_type='cartesian', frame='gcrs')

def create_earth_location(lat_lon_alt):
    return EarthLocation.from_geodetic(lat_lon_alt[1], lat_lon_alt[0], lat_lon_alt[2]) 