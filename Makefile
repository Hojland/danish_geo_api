.PHONY: build start_dev push_image

aws_login:
	$(eval export AWS_PROFILE=$(shell bash -c 'read -p "Enter AWS_PROFILE: " pass; echo $$pass'))
	$(eval export AWS_DEFAULT_REGION=$(shell bash -c 'read -p "Enter AWS_DEFAULT_REGION: " pass; echo $$pass'))

get_danish_osrm:
	wget http://download.geofabrik.de/europe/denmark-latest.osm.pbf -O data/denmark-latest.osm.pbf

preprocess_osrm:
	docker run -t -v "${PWD}/data/:/data/" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/denmark-latest.osm.pbf
	docker run -t -v "${PWD}/data/:/data/" osrm/osrm-backend osrm-partition /data/denmark-latest.osrm
	docker run -t -v "${PWD}/data/:/data/" osrm/osrm-backend osrm-customize /data/denmark-latest.osrm

run_server:
	docker run -t -i -p 5000:5000 -v "${PWD}/data/:/data/" osrm/osrm-backend osrm-routed --algorithm mld /data/denmark-latest.osrm

frontend:
	docker run -p 9966:9966 osrm/osrm-frontend
	xdg-open 'http://127.0.0.1:9966'

start_dev:
	@-PWD=$(shell pwd)
	@-docker stop distance_api > /dev/null 2>&1 ||:
	@-docker container prune --force > /dev/null

	@-docker build -f dev.Dockerfile . \
		--no-cache -t distance_api:latest

	@-docker run \
		-p 10000:8888 \
		--rm \
		--name distance_api \
		--cpus=1 \
		-v $(PWD)/distance_api/:/app/src/ \
		-d \
		distance_api:latest > /dev/null

	@echo "Container started"
	@echo "Jupyter is running at http://localhost:10000/?token=dist"

build_osm2psql:
	docker build -f Dockerfile . -t  osm2pgsql:latest

ingest_data:
	$(eval export POSTGIS_PSW=$(shell bash -c 'read -p "Enter POSTGIS PASSWORD: " pass; echo $$pass'))
	docker run -i -t --rm osm2pgsql:latest -c 'osm2pgsql --create --slim --cache 2000 --database postgis --username mart --password --host pd1502vu308r3fz.civyps8uzncb.eu-central-1.rds.amazonaws.com --port 5432 /data/denmark-latest.osm.pbf'