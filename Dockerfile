# DOCKER-VERSION 1.5.0
# VERSION 0.2

FROM debian:latest

COPY /data/denmark-latest.osm.pbf /data/denmark-latest.osm.pbf
RUN apt-get update && apt-get install -y \
    make \
    cmake \
    g++ \
    git-core \
    libboost-dev \
    libboost-system-dev \
    libboost-filesystem-dev \
    libexpat1-dev \
    zlib1g-dev \
    libbz2-dev \
    libpq-dev \
    libproj-dev \
    lua5.3 \
    liblua5.3-dev

RUN git clone https://github.com/openstreetmap/osm2pgsql.git &&\
    cd osm2pgsql && \
    mkdir build &&\
    cd build &&\
    cmake .. &&\
    make &&\
    make install &&\
    cd /root &&\
    rm -rf build

ENTRYPOINT ["/bin/bash"]