import math
from pyproj import Proj
import models.schemas as schemas
from models.SimplePoint import SimplePoint
import constants
import dive_data_helper
#
# construct using polar coordinates
# Where degree is the compass heading
# Where distanceFt is the distance of the line in Feet.
# Use getX() and getY() to convert to cartesian notation
# prevLine is a reference to the line that came before if we are plotting a line with multiple directions.
class DivePointInterest:
    def __init__(self,name, ref_point, depth_reading_ft, date, time, tide_height_ft, tide_height_target_ft, line_heading_deg, magnetic_declination_deg, distance_to_ref_point_ft, description):
        #projection for zone in st andrews
        self.proj = Proj(constants.PROJECTION)
        self.name = name
        self.ref_point = ref_point
        self.depth_reading_ft = depth_reading_ft
        self.time = time
        self.date = date
        self.tide_height_ft = tide_height_ft
        self.tide_height_target_ft = tide_height_target_ft
        self.line_heading_deg = line_heading_deg
        self.magnetic_declination_deg = magnetic_declination_deg
        self.distance_to_ref_pt_ft = distance_to_ref_point_ft
        self.description = description

        self.point_depth_adjustment_ft = self.tide_height_target_ft - self.tide_height_ft
        self.depth_adjusted_ft = self.depth_reading_ft + self.point_depth_adjustment_ft
        self.line_heading_adjusted_deg = self.line_heading_deg + self.magnetic_declination_deg

    def recalculate_calculated_values(self):
        self.point_depth_adjustment_ft = self.tide_height_target_ft - self.tide_height_ft
        self.depth_adjusted_ft = self.depth_reading_ft + self.point_depth_adjustment_ft
        self.line_heading_adjusted_deg = self.line_heading_deg + self.magnetic_declination_deg

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_depth_reading_ft(self):
            return self.depth_reading_ft

    def set_depth_reading_ft(self, depth_reading_ft):
            self.depth_reading_ft = depth_reading_ft

    def get_time(self):
        return self.line_time

    def get_date(self):
        return self.date

    def get_tide_height_ft(self):
            return self.tide_height_ft

    def get_tide_height_target_ft(self):
        return self.tide_height_target_ft

    def get_line_heading_deg(self):
        return self.line_heading_deg

    def get_magnetic_declination_deg(self):
        return self.magnetic_declination_deg

    def get_distance_to_ref_pt_ft(self):
        return self.distance_to_ref_pt_ft

    def get_distance_to_ref_pt_meters(self):
        return self.distance_to_ref_pt_ft / 3.281

    def get_description(self):
            return self.description

    def set_description(self, description):
            self.description = description

    def get_point_depth_adjustment_ft(self):
        return self.point_depth_adjustment_ft

    def get_depth_adjusted_ft(self):
            return self.depth_adjusted_ft

    def get_ref_point(self):
        return self.ref_point

    def get_line_heading_adjusted_deg(self):
        return self.line_heading_adjusted_deg

    def get_ref_point_utm_northing_19t(self):
        return self.ref_point_utm_northing_19t

    def get_schema(self):
        return schemas.dive_point_of_interest

    def get_x(self):
        #print("Deg=" + str(self.degree))
        #print("cos(Deg) for X "+str(round(math.sin(math.radians(self.degree)))))
        #print("X Before add" + str(round(math.sin(math.radians(self.degree))*self.getDistanceMeters())))
        if self.ref_point is not None:
            #print("Prev Point X: "+ str(self.prevLine.getX()))
            #print("End Result X:"+str(self.prevLine.getX()+round(math.sin(math.radians(self.degree))*self.getDistanceMeters(),0)))
            return self.ref_point.get_x()+round(math.sin(math.radians(self.line_heading_adjusted_deg))*self.get_distance_to_ref_pt_meters(),0)
        else:
            return round(math.sin(math.radians(self.line_heading_adjusted_deg))*self.get_distance_to_ref_pt_meters(),0)

    def get_y(self):
        #print("Deg=" + str(self.degree))
        #print("sin(Deg) for Y "+str(round(math.cos(math.radians(self.degree)))))
        #print("Y Before add" + str(round(math.cos(math.radians(self.degree))*self.getDistanceMeters())))
        if self.ref_point is not None:
            #print("Prev Point Y: "+ str(self.prevLine.getY()))
            #print("end result Y: " + str(self.prevLine.getY()+round(math.cos(math.radians(self.degree))*self.getDistanceMeters(),0)))
            return self.ref_point.get_y()+round(math.cos(math.radians(self.line_heading_adjusted_deg))*self.get_distance_to_ref_pt_meters(),0)
        else:
            return round(math.cos(math.radians(line_heading_adjusted_deg.degree))*self.get_distance_to_ref_pt_meters(),0)


    def to_long_lat(self):
        lon, lat = self.proj(self.get_x(), self.get_y(), inverse=True)
        return (lon,lat)


    def to_point_row_dict(self):
        ref_point_x = 0.0
        ref_point_y = 0.0
        if self.ref_point is not None:
            ref_point_x = self.ref_point.get_x()
            ref_point_y = self.ref_point.get_y()
        return {
            'geometry' :
                {
                    'type':'Point',
                    'coordinates': self.to_long_lat()
                },
            'properties':
                {
                    'name': self.name,
                    'date': self.date,
                    'time': self.time,
                    'tideHeightFt': self.tide_height_ft,
                    'tideHeightTargetFt': self.tide_height_target_ft,
                    'pointDepthAdjustmentFt': self.point_depth_adjustment_ft,
                    'depthReadingFt': self.depth_reading_ft,
                    'depthAdjustedFt': self.depth_adjusted_ft,
                    'distanceToRefPtFt': self.distance_to_ref_pt_ft,
                    'lineHeadingDeg': self.line_heading_deg,
                    'magneticDeclinationDeg': self.magnetic_declination_deg,
                    'lineHeadingAdjustedDeg': self.line_heading_adjusted_deg,
                    'refPointUTMEasting19T': ref_point_x,
                    'refPointUTMNorthing19T': ref_point_y,
                    'description': self.description,
                },
            }



