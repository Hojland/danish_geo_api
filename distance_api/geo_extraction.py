#import xml.etree.ElementTree as ET
from collections import Counter
import pandas as pd
from IPython.display import display, HTML
import esy.osm.pbf

def main():
    #tree = ET.parse('/app/data/pbf/denmark_wgs-84_2020-09-09_pbf_full-detail.pbf')
    osm = esy.osm.pbf.File('/app/data/pbf/denmark_wgs-84_2020-09-09_pbf_full-detail.pbf')
    osm = esy.osm.pbf.File('/app/data/denmark-latest.osm.pbf')
    parks = [entry for entry in osm if entry.tags.get('leisure') == 'park']

    count = 0
    for entry in osm:
        print(entry)
        count += 1
        if count > 1:
            break


    nodes = []
    tag_stats = []
    for idx, child in enumerate(tree.getroot()):
        if child.tag == 'node':
            new_node = {
                'node_id': child.attrib['id'],
                'is_busstop': False,
                'is_trainstop': False,
                'is_subway': False,
                'is_highwayaccess': False,
                'name': None,
                'lat': child.attrib['lat'],
                'lon': child.attrib['lon'],
            }
            new_node['quicklink'] = '<a href="https://www.google.com/maps?q={}+{}">Link</a>'.format(new_node['lat'], new_node['lon'])
    #        new_node['quicklink'] = 'https://www.google.com/maps?q={}+{}'.format(new_node['lat'], new_node['lon'])

    #        print(child.tag, child.attrib)
            new_node['is_busstop'] = is_busstop([sub_child.attrib for sub_child in child])
            new_node['is_trainstop'] = is_trainstop([sub_child.attrib for sub_child in child])
            new_node['is_subway'] = is_subway([sub_child.attrib for sub_child in child])
            new_node['is_highwayaccess'] = is_highwayaccess([sub_child.attrib for sub_child in child])
            names = [sub_child.attrib['v'] for sub_child in child if sub_child.attrib['k'] == 'name']
            new_node['name'] = names[0] if names else ''
            nodes.append(new_node)

            # Debugging
            if child.attrib['id'] in []:
                print(child.attrib)
                for each in child:
                    print(each.attrib)
                print('___')
    df = pd.DataFrame(nodes)
    df.describe()
    df.to_csv('nordic_public_transport.csv')

if __name__ == '__main__':
    main()

def is_busstop(tags):
    for tag in tags:
        if tag.get('k') == 'bus' and tag.get('v') == 'yes':
            return True
        if tag.get('k') == 'highway' and tag.get('v') == 'bus_stop':
            return True
    return False

def is_trainstop(tags):
    for tag in tags:
        if tag.get('k') == 'train' and tag.get('v') == 'yes':
            return True
        if tag.get('k') == 'railway' and tag.get('v') in ['stop', 'station']:
            return True
        if tag.get('k') == 'light_rail' and tag.get('v') == 'yes':
            return True
    return False

def is_subway(tags):
    for tag in tags:
        if tag.get('k') == 'subway' and tag.get('v') == 'yes':
            return True
    return False

def is_highwayaccess(tags):
    for tag in tags:
        if tag.get('k') == 'highway' and tag.get('v') == 'motorway_junction':
            return True
    return False