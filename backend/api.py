from ninja import NinjaAPI
import requests
import json
import random
from math import sqrt

from .utils import haversine_dist
from .graph import Graph
from .new_routing_algos import Router
from .yelp_query import YelpFusion

api       = NinjaAPI()
osm_url   = 'http://overpass-api.de/api/interpreter'
n_latblks = 50
n_lngblks = 50
time      = 3000

@api.get("/routing/{n1_lat}/{n1_lng}/{n2_lat}/{n2_lng}")
def routing(request, 
            n1_lat: float, 
            n1_lng: float, 
            n2_lat: float, 
            n2_lng: float):

    road_network = Graph()
    # find roads near origin, destination, and bounding box btwn origin, dest.
    south, north = min(n1_lat, n2_lat), max(n1_lat, n2_lat)
    west, east = min(n1_lng, n2_lng), max(n1_lng, n2_lng)
    osm_ways = requests.get(osm_url, params={'data': f"""
        [out:json][timeout:600];
        way['highway'](around: 100, {n1_lat}, {n1_lng});
        way['highway'](around: 100, {n2_lat}, {n2_lng});
        way['highway']({south}, {west}, {north}, {east});
        out geom;
    """}).json()["elements"]
    road_network.add_ways(osm_ways)

    router = Router(road_network, n_latblks, n_lngblks)
    result = router.mutually_reachable(n1_lat, n1_lng, n2_lat, n2_lng, time)

    # yelp query
    valid = []
    for i in range(n_latblks):
        for j in range(n_lngblks):
            if result[0][i][j]:
                valid.append((i, j))

    i, j = random.choice(valid) if len(valid) > 0 else (0, 0)
    print(i, j, result[1] + (i+0.5)*result[3], result[2] + (j+0.5)*result[4])

    yelp_api = YelpFusion()
    business_json = yelp_api.business_search(params={
        'term': 'restaurant',
        'latitude' : result[1] + (i+0.5)*result[3],
        'longitude' : result[2] + (j+0.5)*result[4],
        'radius': 1609 * int(haversine_dist(result[1] + i*result[3], result[2] + j*result[4],
                                     result[1] + (i+1)*result[3], result[2] + (j+1)*result[4]) / 2),
        'limit': 1,
    })['businesses'][0]

    print(business_json)

    return { 'isochrone': result[0], 
             'minlat'   : result[1],
             'minlng'   : result[2],
             'd_lat'    : result[3],
             'd_lng'    : result[4],
             'business' : business_json }


@api.post("/update/isochrone")
def update_isochrone(request,
                     nlatblks: int = None,
                     nlngblks: int = None,
                     isotime : int = None):
    """ Update parameters used in isochrone calculation.
    """
    global n_latblks, n_lngblks, time
    if nlatblks is not None:
        n_latblks = nlatblks
    if nlngblks is not None:
        n_lngblks = nlngblks
    if isotime is not None:
        time = isotime
