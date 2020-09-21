"""The Point class."""


class Point(object):
    def __init__(self, latitude, longitude, name=None):
        """Constructor."""
        if not 71 > latitude > 54:
            raise Exception('All points must be in Scandinavia')
        if not 32 > longitude > 4:
            raise Exception('All points must be in Scandinavia')

        self.lat = latitude
        self.lon = longitude
        self.name = name

    def __str__(self):
        if self.name:
            return '<Point latitude={}, longitude={}, name={}>'.format(
                self.lat,
                self.lon,
                self.name or ''
            )
        else:
            return '<Point latitude={}, longitude={}>'.format(
                self.lat,
                self.lon
            )

    def __repr__(self):
        return self.__str__(self)
