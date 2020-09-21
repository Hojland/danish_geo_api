"""dawa tools"""
import numpy
import requests
import jmespath


def wash(address):
    r = requests.get(
        'https://dawa.aws.dk/datavask/adgangsadresser',
        params=[('betegnelse', address)],
        )
    json_r = r.json()
    result = jmespath.search('resultater[*].adresse.id', json_r)
    return result[0]


def coordinates_acc(acc_add_id):
    r = requests.get(
        'https://dawa.aws.dk/adgangsadresser',
        params={'id': acc_add_id,
               'struktur': 'mini'
               })
    json_r = r.json()
    lat = jmespath.search('y', json_r[0])
    lon = jmespath.search('x', json_r[0])
    return lat, lon