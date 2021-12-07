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
class DivePoint:
    def __init__(self, dive_data, dive_num, line_num, point_num, is_extrapolated):
        #projection for zone in st andrews
        self.proj = Proj(constants.PROJECTION)
        dive, line, point = dive_data_helper.lookup_dive_line_point(dive_data, dive_num, line_num, point_num)
        self.dive_number = dive["number"]
        self.line_number = line["number"]
        self.reel_length_mark_ft = point['reelLengthMarkFt']
        self.name = "dive{}-line{}-pt{}".format(self.dive_number, self.line_number, self.reel_length_mark_ft)
        self.line_time = line['time']
        self.date = dive['date']
        self.line_distance_to_ref_pt_ft = line['distanceToRefPtFt']
        self.distance_to_ref_pt_ft = self.line_distance_to_ref_pt_ft + self.reel_length_mark_ft
        self.tide_height_ft = line['tideHeightFt']
        self.tide_height_target_ft = dive_data['tideHeightTargetFt']
        self.point_depth_adjustment_ft = self.tide_height_target_ft - self.tide_height_ft
        self.depth_reading_ft = point['depthReadingFt']
        self.depth_adjusted_ft = self.depth_reading_ft + self.point_depth_adjustment_ft
        self.line_heading_deg = line['headingDeg']
        self.magnetic_declination_deg = dive_data['magneticDeclinationDeg']
        self.line_heading_adjusted_deg = self.line_heading_deg + self.magnetic_declination_deg
        self.ref_point_utm_easting_19t = dive_data['refPointUTMEasting19T']
        self.ref_point_utm_northing_19t = dive_data['refPointUTMNorthing19T']
        self.ref_point = SimplePoint(self.ref_point_utm_easting_19t, self.ref_point_utm_northing_19t,None)
        self.extrapolated = is_extrapolated

        if 'note' in point:
            self.note = point['note']
        else:
            self.note = 'N/A'

        if 'styleName' in point:
            self.styleName = point['styleName']
        else:
            self.styleName = 'default-point'


    def recalculate_calculated_values(self):
        self.name = "dive{}-line{}-pt{}".format(self.dive_number, self.line_number, self.reel_length_mark_ft)
        self.distance_to_ref_pt_ft = self.line_distance_to_ref_pt_ft + self.reel_length_mark_ft
        self.point_depth_adjustment_ft = self.tide_height_target_ft - self.tide_height_ft
        self.depth_adjusted_ft = self.depth_reading_ft + self.point_depth_adjustment_ft
        self.line_heading_adjusted_deg = self.line_heading_deg + self.magnetic_declination_deg

    def get_dive_number(self):
        return self.dive_number

    def get_line_number(self):
        return self.dive_number

    def get_point_number(self):
        return self.point_number

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_line_time(self):
        return self.line_time

    def get_date(self):
        return self.date

    def get_reel_length_mark_ft(self):
        return self.reel_length_mark_ft

    def set_reel_length_mark_ft(self, reel_length_mark_ft):
        self.reel_length_mark_ft = reel_length_mark_ft

    def get_distance_to_ref_pt_ft(self):
        return self.distance_to_ref_pt_ft

    def get_distance_to_ref_pt_meters(self):
        return self.distance_to_ref_pt_ft / 3.281

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

    def get_ref_point(self):
        return self.ref_point

    def get_line_heading_deg(self):
            return self.line_heading_deg
    def get_magnetic_declination_deg(self):
        return self.magnetic_declination_deg

    def get_line_heading_adjusted_deg(self):
        return self.line_heading_adjusted_deg

    def get_depth_reading_ft(self):
        return self.depth_reading_ft

    def set_depth_reading_ft(self, depth_reading_ft):
        self.depth_reading_ft = depth_reading_ft

    def get_depth_adjusted_ft(self):
        return self.depth_adjusted_ft

    def get_schema(self):
        return schemas.dive_line_point

    def is_extrapolated(self):
        return self.extrapolated

    def set_extrapolated(self, extrapolated):
        self.extrapolated = extrapolated

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
            return round(math.cos(math.radians(self.line_heading_adjusted_deg))*self.get_distance_to_ref_pt_meters(),0)


    def to_long_lat(self):
        lon, lat = self.proj(self.get_x(), self.get_y(), inverse=True)
        return (lon,lat)


    def to_point_row_dict(self):
        return {
            'geometry' :
                {
                    'type':'Point',
                    'coordinates': self.to_long_lat()
                },
            'properties':
                {
                    'name': self.name,
                    'diveNumber': self.dive_number,
                    'lineNumber': self.line_number,
                    'date': self.date,
                    'lineTime': self.line_time,
                    'tideHeightFt': self.tide_height_ft,
                    'tideHeightTargetFt': self.tide_height_target_ft,
                    'pointDepthAdjustmentFt': self.point_depth_adjustment_ft,
                    'depthReadingFt': self.depth_reading_ft,
                    'depthAdjustedFt': self.depth_adjusted_ft,
                    'reelLengthMarkFt': self.reel_length_mark_ft,
                    'distanceToRefPtFt': self.distance_to_ref_pt_ft,
                    'lineHeadingDeg': self.line_heading_deg,
                    'magneticDeclinationDeg': self.magnetic_declination_deg,
                    'lineHeadingAdjustedDeg': self.line_heading_adjusted_deg,
                    'refPointUTMEasting19T': self.ref_point_utm_easting_19t,
                    'refPointUTMNorthing19T': self.ref_point_utm_northing_19t,
                    'isExtrapolated': str(self.extrapolated),
                    'note': self.note,
                    'styleName': self.styleName
                },
            }