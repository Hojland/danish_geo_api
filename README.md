# distance_api

Alternative to hvorlangterder.dk

## App flow

* When the app is initiated the public transport lists is loaded into memory in the variables `app.bus_stops`, `app.subway_stops`, etc.
* The app has two endpoints:
  * `/nearest`
    * This endpoint returns distance and traveltime to nearest POI
    * All the datapoints are filtered using the `filter_points`, that uses a bounding box to filter out point far away.
    * Each of the points remaining is sent to OSRM for routing to get distance and traveltime
    * The closest match is returned from the API
  * `/ptp` (point to point)
    * The points are sent to OSRM for routing to get distance and travel time.

## Update bus stops

* Download new dataset from: https://osmaxx.hsr.ch/
* ...

## Deploying

* A bitbucket pipeline is setup to deploy the code to the production server. See the file `bitbucket-pipelines.yml` for details.
* The pipeline runs the script `deploy.sh` on the server

## osrm-frontend on the hosted routing machine

A visual too to see the routing by the OSRM backend

* `docker run --rm -p 9966:9966 -e OSRM_BACKEND='http://159.89.11.45:5000' osrm/osrm-frontend`


We can delete full pbf map.

https://pypi.org/project/esy-osmfilter/