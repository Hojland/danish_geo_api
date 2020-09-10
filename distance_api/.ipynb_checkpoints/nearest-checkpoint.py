"""Nearest calculation tools."""
import math
import time
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor

import numpy
import requests

from distance_api.point import Point


def get_degree_length(lat, _):
    """Return the lenght in km for each lat an lon at the given point."""
    rad = math.cos(lat * math.pi / 180)
    return {
        'lon_length': 111.32 * rad * 1000,
        'lat_length': 111 * 1000
    }


def subset_dataset(point_a, point_b, boxsize=10000):
    """Return bool, whether point is inside major bounding box."""
    # get length of a degree
    degree_lengths = get_degree_length(point_a.lat, point_a.lon)

    # boxsize / length = degrees
    lon_border_width = boxsize / degree_lengths['lon_length']
    lat_border_width = boxsize / degree_lengths['lat_length']

    return all([
        point_a.lat > point_b.lat - lat_border_width,
        point_a.lat < point_b.lat + lat_border_width,
        point_a.lon > point_b.lon - lon_border_width,
        point_a.lon < point_b.lon + lon_border_width,
    ])


def eu_dist(point_a, point_b):
    return numpy.sqrt(sum([(point_b.lat - point_a.lat)**2, (point_b.lon - point_a.lon)**2]))


def load_busstops():
    """Load busstops from disk."""
    return load_pointsfile('bus_stops.csv')


def load_trainstops():
    """Load trainstops from disk."""
    return load_pointsfile('train_stops.csv')


def load_subwaystops():
    """Load subwaystops from disk."""
    return load_pointsfile('subway_stops.csv')


def load_highways():
    """Load highway file from disk."""
    return load_pointsfile('highway_access.csv')


def load_pointsfile(filename):
    """Load pointsfile from disk."""
    points = []
    with open('data/{}'.format(filename)) as pointsfile:
        line = pointsfile.readline()
        while line:
            try:
                lat, lon, name = line.split(',', 2)
                name = name.rstrip('\n')
            except ValueError:
                print(line)
                lat, lon = line.split(',')
            points.append(Point(latitude=float(lat), longitude=float(lon), name=name))
            line = pointsfile.readline()
    return points


def point_to_point(start_point, end_point, steps=False):
    """Get distance and duration between to points."""
    router_ip = '159.89.11.45'
    router_port = '5000'
    base_url = 'http://{ip}:{port}'.format(ip=router_ip, port=router_port)
    path = '/route/v1/car/{lon_from},{lat_from};{lon_to},{lat_to}?steps={steps}&alternatives=false'
    url = base_url + path.format(
        lon_from=start_point.lon,
        lat_from=start_point.lat,
        lat_to=end_point.lat,
        lon_to=end_point.lon,
        steps=str(steps).lower()
    )
    resp = requests.get(url).json()
    maneuvers = []
    if steps:
        for man in resp['routes'][0]['legs'][0]['steps']:
            lon, lat = man['maneuver']['location']
            maneuvers.append((lon, lat))
        return resp['routes'][0]['distance'], resp['routes'][0]['duration'], end_point, maneuvers
    return resp['routes'][0]['distance'], resp['routes'][0]['duration'], end_point


def filter_points(starting_point, points):
    """Coarsely filter a set of points by bounding box and euclidian distance."""
    start = time.time()
    filtered_stops = []
    boxsize = 1000
    while len(filtered_stops) < 25:
        for stop in points:
            if subset_dataset(starting_point, stop, boxsize=boxsize):
                filtered_stops.append(stop)
        boxsize = boxsize + 10000  # search in 10km steps
    print(len(filtered_stops))
    print('BB filtering took {:.3f} seconds'.format(time.time() - start))

    # # Foreach in remaining bus stops: Do euclidian filter
    # start = time.time()
    # eu_filtered_stops = []
    # for stop in filtered_stops:
    #     if eu_dist(starting_point, stop) < 0.1:
    #         eu_filtered_stops.append(stop)

    # print('EU filtering took {:.3f} seconds'.format(time.time() - start))
    # return eu_filtered_stops
    return filtered_stops


def get_nearest(starting_point, points, steps=False):
    """Given starting_point, find the nearest neighbor in points."""
    # Foreach in remain bus stops: Do osrm-routed distance/duration
    start = time.time()
    closest = {
        'point': None,
        'distance': 999999,
        'duration': 999999
    }

    # Concurrency FTW
    with ThreadPoolExecutor(max_workers=200) as executor:
        futures = []
        for each in points:
            futures.append(executor.submit(point_to_point, starting_point, each, steps))
        for future in as_completed(futures):
            if steps:
                distance, duration, end_point, maneuvers = future.result()
            else:
                distance, duration, end_point = future.result()
            if duration < closest['duration']:
                # Set new closest
                closest = {
                    'point': {'lat': end_point.lat, 'lon': end_point.lon},
                    'distance': int(distance),
                    'duration': int(duration),
                }
                if steps:
                    closest['maneuvers'] = maneuvers
                if end_point.name:
                    closest['name'] = end_point.name

    avg = (time.time() - start) / max(len(points), 1)
    print('Distance calc took {:.3f} seconds (Avg: {:.3f} s pr. point)'.format(
        time.time() - start,
        avg
    ))
    return closest
