"""Main app module."""
from flask import Flask, jsonify, send_from_directory
from webargs import fields
from webargs.flaskparser import use_kwargs

from distance_api.point import Point
from distance_api.nearest import get_nearest
from distance_api.nearest import filter_points
from distance_api.nearest import load_busstops
from distance_api.nearest import load_trainstops
from distance_api.nearest import load_subwaystops
from distance_api.nearest import load_highways
from distance_api.nearest import point_to_point
from distance_api import dawa

def setup_app():
    """Load needed dataset to memory."""
    app.bus_stops = load_busstops()
    app.train_stops = load_trainstops()
    app.subway_stops = load_subwaystops()
    app.highway = load_highways()
    print('Bus stops: {}, Train stops: {}, Subway stops: {}, Highways: {}'.format(
        len(app.bus_stops),
        len(app.train_stops),
        len(app.subway_stops),
        len(app.highway)
    ))


app = Flask(__name__)
setup_app()

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route("/ptp", methods=['POST'])
@use_kwargs({
    'lat_from': fields.Float(
        required=True,
        validate=lambda val: 71 > val > 54
    ),
    'lon_from': fields.Float(
        required=True,
        validate=lambda val: 32 > val > 4
    ),
    'lat_to': fields.Float(
        required=True,
        validate=lambda val: 71 > val > 54
    ),
    'lon_to': fields.Float(
        required=True,
        validate=lambda val: 32 > val > 4
    ),
})
def ptp(lat_from, lon_from, lat_to, lon_to):
    """Simple endpoint to get info from point to point."""
    dist, dur, _ = point_to_point(Point(lat_from, lon_from), Point(lat_to, lon_to))
    res = {
        'distance': dist,
        'duration': dur,
    }
    return jsonify(res)

@app.route("/ata", methods=['POST'])
@use_kwargs({
    'address_from': fields.Str(
        required=True
    ),
    'address_to': fields.Str(
        required=True
    )
})
def add_t_add(address_from, address_to):
    '''Get address to address time''' 
    id_from = dawa.wash(address_from)
    id_to = dawa.wash(address_to)
   
    lat_from, lon_from = dawa.coordinates_acc(id_from)
    lat_to, lon_to = dawa.coordinates_acc(id_to)

    dist, dur, _ = point_to_point(Point(lat_from, lon_from), Point(lat_to, lon_to))
    res = {
        'distance': dist,
        'duration': dur,
    }
    return jsonify(res)


# def simple_debugger(result, lat_from, lon_from):
#     """:"""
#     import os
#     final_string = '{},{},{}'.format(
#         lat_from,
#         lon_from,
#         'starting_point\n'
#     )
#     for key in result:
#         line = '{},{},{}{}'.format(
#             result[key]['point']['lat'],
#             result[key]['point']['lon'],
#             key,
#             os.linesep,
#         )
#         final_string += line
#     print(final_string)


@app.route("/nearest", methods=['POST'])
@use_kwargs({
    'lat_from': fields.Float(
        required=True,
        validate=lambda val: 71 > val > 54
    ),
    'lon_from': fields.Float(
        required=True,
        validate=lambda val: 32 > val > 4
    ),
    'steps': fields.Boolean(
        required=False,
        missing=False
    ),
})
def nearest(lat_from, lon_from, steps=False):
    """Get nearest POI from point."""
    starting_point = Point(latitude=lat_from, longitude=lon_from)
    # pseudo
    # Bounding box filter bus stops.

    filtered_bus_stops = filter_points(starting_point, app.bus_stops)
    closest_bus = get_nearest(starting_point, filtered_bus_stops, steps)

    filtered_train_stops = filter_points(starting_point, app.train_stops)
    closest_train = get_nearest(starting_point, filtered_train_stops, steps)

    filtered_subway_stops = filter_points(starting_point, app.subway_stops)
    closest_subway = get_nearest(starting_point, filtered_subway_stops, steps)

    filtered_highway = filter_points(starting_point, app.highway)
    closest_highway = get_nearest(starting_point, filtered_highway, steps)

    # Foreach in remain bus stops: Do osrm-routed distance/duration
    closest = {
        'bus': closest_bus,
        'train': closest_train,
        'subway': closest_subway,
        'highway': closest_highway,
    }
    # simple_debugger(closest, lat_from, lon_from)

    # Return closest bus stop
    return jsonify(closest)


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)