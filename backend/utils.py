from math import radians, cos, sin, asin, sqrt, inf

DEFAULT_SPEED = 30

def haversine_dist(lat1, lon1, lat2, lon2, metric="mi"):
    lat1, lat2 = radians(lat1), radians(lat2)
    lon1, lon2 = radians(lon1), radians(lon2)
    c = sin((lat2-lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2-lon1)/2)**2
    c = 2 * asin(sqrt(c))
    return c * 3956 if metric == "mi" else c * 6371


def in_bounds(x, a, b) -> bool:
    """ Returns True if a <= x <= b, False otherwise.
    """
    return True if a <= x and x <= b else False