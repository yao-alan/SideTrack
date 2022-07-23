import typing
from queue import PriorityQueue
from math import inf

from .graph import Graph
from .utils import haversine_dist, in_bounds, DEFAULT_SPEED

class Router:
    # reminder: grid treats (i, j) as (lat, lng)
    def __init__(self, 
                 g: Graph,
                 n_latblks: int = 100,
                 n_lngblks: int = 100):
        # self.grid[i][j]['edges_out'][k] = kth edge out of (i, j)
        # self.grid[i_2][j_2]['time_to_reach'][(i_1, j_1)] = time from (i_1, j_1)->(i_2, j_2)
        self.grid = [[{
            'edges_out': [],
            'time_to_reach': {}
        } for j in range(n_lngblks+1)] for i in range(n_latblks+1)]

        self.n_latblks = n_latblks
        self.n_lngblks = n_lngblks
        self.bleft = g.bleft
        self.tright = g.tright
        self.walk_speed = 3

        # approx. time to traverse a grid block (assuming 3 mph walking speed)
        self.walktime = haversine_dist(self.bleft['lat'], self.bleft['lng'],
                                       self.tright['lat'], self.tright['lng']) \
                                       * 3600 / (self.walk_speed * n_latblks)
        # approx time to drive across a grid block
        self.drivetime = haversine_dist(self.bleft['lat'], self.bleft['lng'],
                                        self.tright['lat'], self.tright['lng']) \
                                        * 3600 / (DEFAULT_SPEED * n_latblks)

        # worst-case scenario: walk to neighboring blocks
        for i in range(n_latblks+1):
            for j in range(n_lngblks+1):
                if i > 0:
                    self.grid[i][j]['edges_out'].append((i-1, j, self.walktime))
                if i < n_latblks:
                    self.grid[i][j]['edges_out'].append((i+1, j, self.walktime))
                if j > 0:
                    self.grid[i][j]['edges_out'].append((i, j-1, self.walktime))
                if j < n_lngblks:
                    self.grid[i][j]['edges_out'].append((i, j+1, self.walktime))

        # add approximate edges found by raymarching real roads
        for n1_id in g.nodes.keys():
            n1_edges = g.nodes[n1_id]
            for edge in n1_edges:
                lat1, lng1 = edge['start_lat'], edge['start_lng']
                lat2, lng2 = edge['end_lat'], edge['end_lng']

                i1, j1 = self.__get_block(lat1, lng1)
                i2, j2 = self.__get_block(lat2, lng2)

                d_lat = (self.tright['lat'] - self.bleft['lat']) / self.n_latblks
                d_lng = (self.tright['lng'] - self.bleft['lng']) / self.n_lngblks

                march_lat, march_lng = lat1, lng1
                march_i, march_j = i1, j1
                while march_i != i2 or march_j != j2:
                    # if road on grid is vertical
                    if lat1 == lat2:
                        march_j += 1 if lng1 < lng2 else -1
                        march_lng = self.bleft['lng'] + march_j*d_lng
                    # if road on grid is horizontal
                    elif lng1 == lng2:
                        march_i += 1 if lat1 < lat2 else -1
                        march_lat = self.bleft['lat'] + march_i*d_lat
                    else:
                        closest_vert = self.bleft['lat'] + (march_i+1)*d_lat if lat1 < lat2 else \
                                       self.bleft['lat'] + march_i*d_lat
                        closest_horz = self.bleft['lng'] + (march_j+1)*d_lng if lng1 < lng2 else \
                                       self.bleft['lng'] + march_j*d_lng

                        d_vert = closest_vert - march_lat
                        d_horz = closest_horz - march_lng
                        t_vert = abs( d_vert / (lat2-lat1) )
                        t_horz = abs( d_horz / (lng2-lng1) )

                        # intersects with horizontal before vertical (move vertically)
                        if t_horz < t_vert:
                            march_lat += t_horz * (lat2-lat1)
                            march_lng = closest_horz
                            march_j += 1 if lng1 < lng2 else -1
                        # intersects with vertical before horizontal (move horizontally)
                        elif t_vert < t_horz:
                            march_lng += t_vert * (lng2-lng1)
                            march_lat = closest_vert
                            march_i += 1 if lat1 < lat2 else -1
                        # intersects with top right corner (move diagonally)
                        else:
                            march_lat = closest_vert
                            march_lng = closest_horz
                            march_i += 1 if lat1 < lat2 else -1
                            march_lng += 1 if lng1 < lng2 else -1

                    time = (haversine_dist(lat1, lng1, march_lat, march_lng) * 3600 / DEFAULT_SPEED) + self.drivetime
                    #print(time, lat1, lng1, march_lat, march_lng)
                    self.grid[i1][j1]['edges_out'].append((march_i, march_j, time))


    def shortest_paths(self,
                       start_lat: float,
                       start_lng: float,
                       mode: str = 'dijkstra'):
        """ Calculates shortest-path timings for self.grid.
            Used when calculating isochrones.
        """
        start_i, start_j = self.__get_block(start_lat, start_lng)

        if mode == 'dijkstra':
            visited = [[False for j in range(self.n_lngblks+1)] for i in range(self.n_latblks+1)]

            for i in range(self.n_latblks+1):
                for j in range(self.n_lngblks+1):
                    self.grid[i][j]['time_to_reach'][(start_i, start_j)] = inf
            self.grid[start_i][start_j]['time_to_reach'][(start_i, start_j)] = 0
            
            pq = PriorityQueue()
            pq.put((0, start_i, start_j))
            while not pq.empty():
                _, i1, j1 = pq.get()
                if not visited[i1][j1]:
                    t1 = self.grid[i1][j1]['time_to_reach'][(start_i, start_j)]
                    for i2, j2, t2 in self.grid[i1][j1]['edges_out']:
                        if t1 + t2 < self.grid[i2][j2]['time_to_reach'][(start_i, start_j)]:
                            self.grid[i2][j2]['time_to_reach'][(start_i, start_j)] = t1 + t2
                            pq.put((t1+t2, i2, j2))


    def mutually_reachable(self,
                           n1_lat: float,
                           n1_lng: float,
                           n2_lat: float,
                           n2_lng: float,
                           max_time: float) -> typing.Tuple[typing.List, float, float]:
        """ Finds all locations L s.t. (n1_lat, n1_lng) -> L -> (n2_lat, n2_lng)
            takes <= max_time.
        """
        n1_i, n1_j = self.__get_block(n1_lat, n1_lng)
        n2_i, n2_j = self.__get_block(n2_lat, n2_lng)

        if (n1_i, n1_j) not in self.grid[0][0]['time_to_reach']:
            self.shortest_paths(n1_lat, n1_lng)
        if (n2_i, n2_j) not in self.grid[0][0]['time_to_reach']:
            self.shortest_paths(n2_lat, n2_lng)

        valid_grid = [[True if self.grid[i][j]['time_to_reach'][(n1_i, n1_j)] +
                        self.grid[i][j]['time_to_reach'][(n2_i, n2_j)] <= max_time
                        else False for j in range(self.n_lngblks+1)] for i in range(self.n_latblks+1)]
        d_lat = (self.tright['lat'] - self.bleft['lat']) / self.n_latblks
        d_lng = (self.tright['lng'] - self.bleft['lng']) / self.n_lngblks

        return (valid_grid, self.bleft['lat'], self.bleft['lng'], d_lat, d_lng)


    # helper function
    def __get_block(self, lat: float, lng: float) -> typing.Tuple[int, int]:
        row = int ( (lat-self.bleft['lat'])*self.n_latblks / (self.tright['lat']-self.bleft['lat']) )
        col = int ( (lng-self.bleft['lng'])*self.n_lngblks / (self.tright['lng']-self.bleft['lng']) )

        return (row, col)
