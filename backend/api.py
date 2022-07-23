from ninja import NinjaAPI
import requests
import json

from .graph import Graph
from .new_routing_algos import Router

api     = NinjaAPI()
osm_url = 'http://overpass-api.de/api/interpreter'

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

    router = Router(road_network, n_latblks=50, n_lngblks=50)
    result = router.mutually_reachable(n1_lat, n1_lng, n2_lat, n2_lng, 600)

    return { 'isochrone': result[0], 
             'minlat': result[1],
             'minlng': result[2],
             'd_lat': result[3],
             'd_lng': result[4] }
