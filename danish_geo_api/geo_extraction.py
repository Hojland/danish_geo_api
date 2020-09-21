#import xml.etree.ElementTree as ET
from collections import Counter
import pandas as pd
from IPython.display import display, HTML
import esy.osm.pbf

def main():
    osm = esy.osm.pbf.File('/app/data/denmark-latest.osm.pbf')

if __name__ == '__main__':
    main()