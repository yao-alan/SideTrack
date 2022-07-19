import typing
from math import inf

from .utils import haversine_dist, DEFAULT_SPEED

class Graph:
    def __init__(self):
        self.nodes    = {}
        self.way_tags = {}
        # overall graph bounds
        self.bleft    = { 'lat': inf, 'lng': inf }
        self.tright   = { 'lat': -inf, 'lng': -inf }

    def add_ways(self, ways: typing.List):
        def __add_way(self, way):
            """ way is a dict of OSM way data. Notable fields:
                    'id', 'bounds', 'nodes', 'geometry', 'tags'.
            """
            self.bleft['lat']  = min(self.bleft['lat'], way['bounds']['minlat'])
            self.bleft['lng']  = min(self.bleft['lng'], way['bounds']['minlon'])
            self.tright['lat'] = max(self.tright['lat'], way['bounds']['maxlat'])
            self.tright['lng'] = max(self.tright['lng'], way['bounds']['maxlon'])
            self.way_tags[way['id']] = way['tags']

            for i in range(len(way['nodes'])-1):
                n1_id = way['nodes'][i]
                n2_id = way['nodes'][i+1]

                n1_coord = (way['geometry'][i]['lat'], way['geometry'][i]['lon'])
                n2_coord = (way['geometry'][i+1]['lat'], way['geometry'][i+1]['lon'])

                speed = DEFAULT_SPEED
                if 'avgspeed' in way['tags']:
                    speed = float(way['tags']['avgspeed'].split()[0])
                elif 'maxspeed' in way['tags']:
                    speed = float(way['tags']['maxspeed'].split()[0])

                n1_n2_dist = haversine_dist(n1_coord[0], n1_coord[1],
                                            n2_coord[0], n2_coord[1])

                if n1_id not in self.nodes:
                    self.nodes[n1_id] = []
                if n2_id not in self.nodes:
                    self.nodes[n2_id] = []
                
                self.nodes[n1_id].append({
                    'start_lat'  : n1_coord[0],
                    'start_lng'  : n1_coord[1],
                    'end_node_id': n2_id,
                    'end_lat'    : n2_coord[0],
                    'end_lng'    : n2_coord[1],
                    'dist'       : n1_n2_dist,
                    'time'       : (n1_n2_dist / speed) * 3600, # time in seconds
                    'parent'     : None,
                })

                if ('oneway' not in way['tags'] and way['tags']['highway'] != 'motorway') \
                    or way['tags']['oneway'] == 'no':
                    self.nodes[n2_id].append({
                        'start_lat'  : n2_coord[0],
                        'start_lng'  : n2_coord[1],
                        'end_node_id': n1_id,
                        'end_lat'    : n1_coord[0],
                        'end_lng'    : n1_coord[1],
                        'dist'       : n1_n2_dist,
                        'time'       : (n1_n2_dist / speed) * 3600,
                        'parent'     : None,
                    })

        for way in ways:
            __add_way(self, way)
 