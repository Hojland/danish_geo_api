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

## Update with more data

* Download new dataset from: https://osmaxx.hsr.ch/
* ...

## osrm-frontend on the hosted routing machine

A visual too to see the routing by the OSRM backend

* `docker run --rm -p 9966:9966 -e OSRM_BACKEND='http://159.89.11.45:5000' osrm/osrm-frontend`

# docker-osm2pgsql

A Docker image with [osm2pgsql](https://github.com/openstreetmap/osm2pgsql), the tool for importing OpenStreetMap data into a Postgresql database. Intended to be used with [openfirmware/docker-postgres-osm](https://github.com/openfirmware/docker-postgres-osm).

## Build Instructions

Can be built from the Dockerfile:

    # docker build -f Dockerfile -t osm2pgsql:latest

This currently builds osm2pgsql for Debian from a specific tag; see the Dockerfile for the specific version. Alternatively, specify the tag and download the image from the Docker Hub.

## Running osm2pgsql

Once the image is built, you can run a single-use container with osm2pgsql. Args will be passed to bash, so you will have access to environment variables in your run command.

    # docker run -i -t --rm osm2pgsql:latest -c 'osm2pgsql -h'

Importing data into the database:

    # docker run -i -t --rm osm2pgsql:latest -c 'osm2pgsql --create --slim --cache 2000 --database postgis --username mart --host pd1502vu308r3fz.civyps8uzncb.eu-central-1.rds.amazonaws.com --port 5432 /osm/extract.osm.pbf'

For more information on running an import, please see TUTORIAL.markdown. If you have a particular scenario in mind, contact me and I will try to create a guide for that situation.

## Guidelines for using osm2pgsql

The options in the command:
https://github.com/openstreetmap/osm2pgsql/blob/master/docs/osm2pgsql.1

* `-i`: Use an interactive stdin when running this container.
* `-t`: Allocate a pseudo-tty for this container.
* `--rm`: Delete this container when the command is finished. We will use this because we won't need the container anymore when the import finishes as we can always start a new container from the base image.
* `--link postgres-osm:pg`: Link the other running container named `postgres-osm` to this container, under the alias `pg`. This allows us access to that container's ports and data.
* `-v ~/osm:osm`: Mount the directory in our home folder called `osm` inside the container as `/osm`. Allows us to inject data into the container.
* `openformware/osm2pgsql`: The base image for this container.
* `-c`: The command to run inside the container. It will run under a bash shell, which is how we use the environment variables. The single quotes around the next portion are required.
* `--create`: Wipe the postgres database and set it up from a clean slate. This is our first import, so we will do that.
* `--slim`: Store temporary information in the database tables. Useful for setting up diff updates of OSM data later.
* `--hstore`: Store OpenStreetMap tag information in the Postgresql hstore column. If you omit this, you will not have extra tags on your nodes.
* `--cache 2000`: Use 2000MB of RAM as a cache for node information during import. Set this to as high as you can depending on your host RAM, but leave a bit for Postgres and other processes. `osm2pgsql` will fail if the number is too high; if so, try again with a lower number. Having it too low will just slow down the import. Default is 800MB.
* `--number-processes 2`: The number of CPU cores to use during the import. Set to as many CPU cores as you have on the host machine to speed up the import.
* `--database $PG_ENV_OSM_DB`: Use the Postgres database named from the `postgres-osm` container. This is a special feature of Docker that reads it automatically from the other container without you having to specify the value for this container.
* `--username $PG_ENV_OSM_USER`: Use the Postgres database user login named from the `postgres-osm` container.
* `--host pg`: As we linked the `postgres-osm` container to this container under the name `pg`, the hosts file in this container will link the hostname `pg` to the `postgres-osm` container.
* `--port $PG_PORT_5432_TCP_PORT`: This may look weird, but it is also Docker linking the port name from one container to the current one.
* `/osm/city-extract.osm.pbf`: The file to import, as mounted on the container from our home directory's folder.

You should modify the `cache` and `number-processes` values. Each of the values has an effect on the import time. In order, imports are affected by RAM, disk speed, then CPU cores/speed. If you have enough RAM to contain the entirety of the imported database then you should see great speed. For a city import, that number may be as low as a few Gigabytes; for the entire planet, you would need **hundreds** of Gigabytes. Next is having fast disks: having an SSD is highly recommended. If not, a RAID1 or RAID0 (or RAID10) of spinning disks is better than a single disk. Focus on random access speed, as this is a database-limited setup. Finally the number of CPU cores helps, but it has less and less effect after 4/6/8 cores. If you are checking the `top` statistics during the import, you will likely see your host machine is RAM and Disk IO limited.