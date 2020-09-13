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

    #The natural=coastline tag is used to mark the mean high water springs line along the coastline at the edge of the sea.
    coastline = [entry for entry in osm if entry.tags.get("natural") == "coastline" and isinstance(entry, esy.osm.pbf.file.Way)]

    # The natural=beach tag is used to mark a loose geological landform along 
    # the coast or along another body of water consisting of sand, gravel, shingle, pebbles, cobblestones or sometimes shell fragments etc.
    beaches = [entry for entry in osm if entry.tags.get("natural") == "beach" and not isinstance(entry, esy.osm.pbf.file.Node)]

    # Søer og fjorde. 
    lakes = [entry for entry in osm if entry.tags.get("natural") == "water" and entry.tags.get("water") == "lake" and not isinstance(entry, esy.osm.pbf.file.Node)]

    # Google foreslår slev man tager dette med som værende "lakes". Men det ligner mere menneskeskabte basiner det meste af det. 
    landuse_reservoir = [entry for entry in osm if entry.tags.get("landuse")=="reservoir"]

    # River= Åer, streams= Åer der er så smalle at man kan hope over dem.
    river = [entry for entry in osm if entry.tags.get("waterway") in ["river", "stream", "riverbank"] or entry.tags.get("water") == "river"]

    # Bugte. Ved ikke om det er værdifuldt med nu tages det lige med. 
    river = [entry for entry in osm if entry.tags.get("natural") in ["bay"]]

    # National parker
    national_park = [entry for entry in osm if entry.tags.get("boundary") == "national_park"]

    # Park
    park = [entry for entry in osm if entry.tags.get("leisure") == "park"]
    
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