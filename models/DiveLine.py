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
class DiveLine:
    def __init__(self, dive_data, dive_num, line_num):
        #projection for zone in st andrews
        self.proj = Proj(constants.PROJECTION)
        dive, line = dive_data_helper.lookup_dive_line(dive_data, dive_num, line_num)
        self.dive_number = dive["number"]
        self.line_number = line["number"]
        self.name = "dive{}-line{}".format(self.dive_number, self.line_number)
        self.time = line['time']
        self.date = dive['date']
        self.length_ft = 300
        self.distance_to_ref_pt_ft = line['distanceToRefPtFt']
        self.length_adjusted_ft = self.distance_to_ref_pt_ft + self.length_ft
        self.heading_deg = line['headingDeg']
        self.magnetic_declination_deg = dive_data['magneticDeclinationDeg']
        self.heading_adjusted_deg = self.heading_deg + self.magnetic_declination_deg
        self.tide_height_ft = line['tideHeightFt']
        self.tide_height_target_ft = dive_data['tideHeightTargetFt']
        self.point_depth_adjustment_ft = self.tide_height_target_ft - self.tide_height_ft
        #self.prev_line = prev_line
        self.ref_point_utm_easting_19t = dive_data['refPointUTMEasting19T']
        self.ref_point_utm_northing_19t = dive_data['refPointUTMNorthing19T']
        self.ref_point = SimplePoint(self.ref_point_utm_easting_19t, self.ref_point_utm_northing_19t,None)

    def get_dive_number(self):
        return self.dive_number

    def get_line_number(self):
        return self.dive_number

    def get_name(self):
        return self.name

    def get_time(self):
        return self.time

    def get_date(self):
        return self.date

    def get_length_ft(self):
        return self.length_ft
    def get_distance_to_ref_pt_ft(self):
        return self.distance_to_ref_pt_ft

    def get_length_adjusted_ft(self):
        return self.length_adjusted_ft
    def get_length_adjusted_meters(self):
        return self.length_adjusted_ft / 3.281

    def get_heading_deg(self):
        return self.heading_deg
    def get_magnetic_declination_deg(self):
        return self.magnetic_declination_deg

    def get_heading_adjusted_deg(self):
        return self.heading_adjusted_deg

    def get_tide_height_ft(self):
        return self.tide_height_ft

    def get_tide_height_target_ft(self):
        return self.tide_height_target_ft

    def get_point_depth_adjustment_ft(self):
        return self.point_depth_adjustment_ft

    def get_ref_point_utm_easting_19t(self):
        return self.ref_point_utm_easting_19

    def get_ref_point_utm_northing_19t(self):
        return self.ref_point_utm_northing_19t

    def get_points(self):
        return self.points

    def get_point_by_reel_length_mark_ft(self, reel_length_mark_ft):
        print("Searching for point {} in a list of {} points".format(reel_length_mark_ft,str(len(self.points))))
        point_to_return = None
        for point in self.points:
            if point.get_reel_length_mark_ft() == reel_length_mark_ft:
                point_to_return = point
                break
        return point_to_return


    def set_points(self,points):
        self.points = points

    def get_schema(self):
        return schemas.dive_line

    def get_x(self):
        #print("Deg=" + str(self.degree))
        #print("cos(Deg) for X "+str(round(math.sin(math.radians(self.degree)))))
        #print("X Before add" + str(round(math.sin(math.radians(self.degree))*self.getDistanceMeters())))
        if self.ref_point is not None:
            #print("Prev Point X: "+ str(self.prevLine.getX()))
            #print("End Result X:"+str(self.prevLine.getX()+round(math.sin(math.radians(self.degree))*self.getDistanceMeters(),0)))
            return self.ref_point.get_x()+round(math.sin(math.radians(self.heading_adjusted_deg))*self.get_length_adjusted_meters(),0)
        else:
            return round(math.sin(math.radians(self.heading_adjusted_deg))*self.get_length_adjusted_meters(),0)

    def get_y(self):
        #print("Deg=" + str(self.degree))
        #print("sin(Deg) for Y "+str(round(math.cos(math.radians(self.degree)))))
        #print("Y Before add" + str(round(math.cos(math.radians(self.degree))*self.getDistanceMeters())))
        if self.ref_point is not None:
            #print("Prev Point Y: "+ str(self.prevLine.getY()))
            #print("end result Y: " + str(self.prevLine.getY()+round(math.cos(math.radians(self.degree))*self.getDistanceMeters(),0)))
            return self.ref_point.get_y()+round(math.cos(math.radians(self.heading_adjusted_deg))*self.get_length_adjusted_meters(),0)
        else:
            return round(math.cos(math.radians(heading_adjusted_deg.degree))*self.get_length_adjusted_meters(),0)

    def to_vec_list(self):
        vec_list = []
        vec_list.append(self.ref_point)
        vec_list.append(self)
        return vec_list

    def to_coord_list(self):
        return list(map(lambda point: point.to_long_lat(),self.to_vec_list()))

    def to_long_lat(self):
        lon, lat = self.proj(self.get_x(), self.get_y(), inverse=True)
        return (lon,lat)


    def to_line_row_dict(self):
        return {
            'geometry' :
                {
                    'type':'LineString',
                    'coordinates': self.to_coord_list()
                },
            'properties':
                {
                    'name': self.name,
                    'diveNumber': self.dive_number,
                    'lineNumber': self.line_number,
                    'date': self.date,
                    'time': self.time,
                    'lengthFt': self.length_ft,
                    'distanceToRefPtFt': self.distance_to_ref_pt_ft,
                    'lengthAdjustedFt': self.length_adjusted_ft,
                    'headingDeg': self.heading_deg,
                    'magneticDeclinationDeg': self.magnetic_declination_deg,
                    'headingAdjustedDeg': self.heading_adjusted_deg,
                    'tideHeightFt': self.tide_height_ft,
                    'pointDepthAdjustmentFt': self.point_depth_adjustment_ft,
                    'tideHeightTargetFt': self.tide_height_target_ft,
                    'refPointUTMEasting19T': self.ref_point_utm_easting_19t,
                    'refPointUTMNorthing19T': self.ref_point_utm_northing_19t,
                },
            }