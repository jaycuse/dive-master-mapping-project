from pyproj import Proj
import models.schemas as schemas
import constants

class SimplePoint:
    def __init__(self,x,y,relates_to):
        self.x = x
        self.y = y
        self.relates_to = relates_to
        self.proj = Proj(constants.PROJECTION)

    def get_x(self):
        return self.x
    def get_y(self):
        return self.y

    def to_long_lat(self):
        lon, lat = self.proj(self.get_x(), self.get_y(), inverse=True)
        return (lon,lat)

    def get_schema(self):
        return schemas.simple_point

    def to_point_row_dict(self):
            depth = None
            if self.relates_to is not None:
                depth = self.relates_to.get_depth_adjusted_ft()
            return {
                'geometry' :
                    {
                        'type':'Point',
                        'coordinates': self.to_long_lat()
                    },
                'properties':
                    {
                        'depthAdjustedFt': depth
                    },
                }