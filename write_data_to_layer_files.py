#! ./venv/bin/python
import fiona
from pprint import pprint
import json
import os
import constants
import copy

from datetime import datetime
from pathlib import Path
from models.DiveLine import DiveLine
from models.DivePoint import DivePoint
from models.DivePointInterest import DivePointInterest
import models.schemas as schemas
from operator import itemgetter
from models.SimplePoint import SimplePoint
from dive_data_helper import *

def main():
    #projection for zone in st andrews
    #proj = Proj(constant.PROJECTION)
    # datetime object containing current date and time
    now = datetime.now()
    #dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
    dataFile = "DiveData"
    dt_string = now.strftime("%d-%m-%Y-"+dataFile)
    script_loc = os.path.dirname(__file__)
    new_dir = os.path.abspath(os.path.join(script_loc,dt_string))
    print("Saving files to "+new_dir)
    create_or_empty(Path(new_dir))

    # Read collected dive data
    inputFile = "./"+dataFile+".json"
    with open(inputFile,'r') as f:
        dive_data = json.load(f)


    dive_lines = []

    # Step 1, read json data and build object data structure.
    for dive in dive_data['dives']:
        for line in dive['lines']:
            points = []
            line_obj = DiveLine(dive_data,dive['number'],line['number'])
            dive_lines.append(line_obj)
            for point in line['points']:
                points.append(DivePoint(dive_data,dive['number'],line['number'],point['reelLengthMarkFt'],False))
            line_obj.set_points(points)

    # Step 2, extrapolate data points
    # Dive 2 line 3 presents a problem. Datapoints collected were had a tide height that is not an integer
    # all other data points were taken with a whole int as tide heights. For those it's simple to adjust to a
    # common tide hight. However since dive 2 line 3 tide height is 9.5 any adjust ment adds `.5` to the depth
    # making our depths not match the accuracy of our other depth readings (dive computer only shows accuracy to 1 foot)
    # 2 solutions are possible. Either round up to the next whole depth each point. Or extrapolate extra points who's
    # depth is a whole number. Fox example if 2 points side by side have a 1 foot difference, we can extrapolate a point
    # between those 2 where the difference will be `.5`. Allowing us to get a whole number. Lets try the extrapolation route

    # We also have a seperate problem where if we have multiple readings of the same depth in a row.. do we want our relief line
    # to pass in the middle of this or at the first reading.. using middle means we have to add a middle point if the multiple
    # readings is an even number
    for line in dive_lines:
        # test if tide height is not whole number
        print("testing line \"{}\" tide height: {}".format(line.get_name(),line.get_tide_height_ft()))
        # Extrapolate middle
        depth_count = {} # set of counts where key is depth value is number found
        point_to_do = {} # set of key depth, value occurence to add after
        to_duplicate = [] # array of (indexes, reel point) we have to add a point after
        dive_points = line.get_points()
        for point in dive_points:
            if point.get_depth_adjusted_ft() in depth_count:
                depth_count[point.get_depth_adjusted_ft()] = depth_count[point.get_depth_adjusted_ft()] + 1
            else:
                depth_count[point.get_depth_adjusted_ft()] = 1

        for depth, count in depth_count.items():
            if count > 1 and (count % 2) == 0:
                point_to_do[depth] = count / 2 # example for 6 we know to add the point after the 3rd occurence between 3 and 4

        occurrence_count = {} # depth, count
        points_to_add = {} #set of points where key is index of point it should be after
        for i in range(len(dive_points)):
            depth_adj = dive_points[i].get_depth_adjusted_ft()
            # To extrapolate
            if depth_adj in point_to_do:
                if depth_adj not in occurrence_count:
                    occurrence_count[depth_adj] = 1
                else:
                    occurrence_count[depth_adj] = occurrence_count[depth_adj] + 1
                if occurrence_count[depth_adj] == point_to_do[depth_adj]:
                    print("Condition met for extrapolation point")
                    # This means we want to add a dupe after this point
                    dive_point_1 = dive_points[i]
                    dive_point_2 = dive_points[i+1]
                    new_dive_point = copy.deepcopy(dive_point_1)
                    new_dive_point.set_extrapolated(True)
                    new_dive_point.set_reel_length_mark_ft(get_reel_length_mark_ft_between_2_points(dive_point_1,dive_point_2))
                    new_dive_point.recalculate_calculated_values()
                    points_to_add[i+1] = new_dive_point

        if len(points_to_add) > 0:
            added_points = 0
            for (index,new_point) in points_to_add.items():
                dive_points.insert(index+added_points, new_point)
                added_points = added_points + 1
            print("Successfully extrapolated {} points on line {}".format(str(added_points),line.get_name()))
            points_to_add.clear() # clear so we can use again later

        # Extrapolate tide fix
        if line.get_tide_height_ft() % 1 != 0:
            print("line {} is not whole number".format(line.get_name()))
            # try to extrapolate points
            if len(dive_points) > 2: # as long as we have more than 2 points
                print("points to test: {}".format(len(dive_points)))
                for i in range(len(dive_points)-2):
                    dive_point_1 = dive_points[i]
                    depth_1 = dive_point_1.get_depth_adjusted_ft()
                    dive_point_2 = dive_points[i+1]
                    depth_2 = dive_point_2.get_depth_adjusted_ft()
                    #print("Testing for extrapolation point: {} and {}".format(depth_1,depth_2))
                    if (depth_1 % 1) == 0.5 and \
                       (depth_2 % 1) == 0.5 and \
                       depth_2 - depth_1 == 1:
                        print("Condition met for extrapolation point: {} and {}".format(depth_1,depth_2))
                        # This means we can extrapolate a point between 1 and 2
                        #first clone our dive_point_1
                        new_dive_point = copy.deepcopy(dive_point_1)
                        #then adjust some values
                        new_dive_point.set_extrapolated(True)
                        new_dive_point.set_reel_length_mark_ft(get_reel_length_mark_ft_between_2_points(dive_point_1,dive_point_2))
                        new_dive_point.set_depth_reading_ft(get_depth_reading_ft_between_2_points(dive_point_1,dive_point_2))
                        new_dive_point.recalculate_calculated_values()
                        points_to_add[i] = new_dive_point
                if len(points_to_add) > 0:
                    added_points = 0
                    for (index,new_point) in points_to_add.items():
                        dive_points.insert(index+added_points, new_point)
                        added_points = added_points + 1
                    print("Successfully extrapolated {} points on line {}".format(str(added_points),line.get_name()))


    # Step 3, figure out relief lines
    # Step 3.1, rearrange data to simplify work
    # this one will be a bit different than our simple array of lines, will be a dict indexed by line names
    # each item in the dict will be a dict indexed by depth with an array of points as a value. The array
    # of points will be populated in order of it found
    lines_by_name = {}
    point_sets = {} # index is line name, value is array of points

    for line in dive_lines:
        points_by_adjusted_depth = {}
        for point in line.get_points():
            add_to_points_by_adjusted_depth(points_by_adjusted_depth,point.get_depth_adjusted_ft(),point)
        point_sets[line.get_name()] = line.get_points()
        lines_by_name[line.get_name()] = points_by_adjusted_depth

    # Step 3.2 record every depth reading
    all_adjusted_depths = []

    for name, points in point_sets.items():
        for point in points:
            all_adjusted_depths.append(point.get_depth_adjusted_ft())

    # Step 3.3 Sort and remove duplicates
    sorted_unique_adjusted_depths = sorted(set(all_adjusted_depths))

    #pprint(lines_by_name)
    # Step 3.4 finally build relief lines
    relief_lines = {} #by depth
    for adjusted_depth in sorted_unique_adjusted_depths:
        potential_line = []
        for line_name, depths_adjusted_dict in lines_by_name.items():
            if adjusted_depth in depths_adjusted_dict:
                index_to_use = 0
                if len(depths_adjusted_dict[adjusted_depth]) > 1:
                    #work already done to add point in middle if number was even Now we grab middle point by
                    # taking the length and doing a floor division and adding 1 (but since it's 0 based index we don't have to add 1)
                    print("Relief middle pick for line {}".format(line_name))
                    print("Adjusted length {}, Length is = {}".format(str(adjusted_depth),str(len(depths_adjusted_dict[adjusted_depth]))))
                    print("Picking {}".format(str(len(depths_adjusted_dict[adjusted_depth]) // 2 )))
                    index_to_use = len(depths_adjusted_dict[adjusted_depth]) // 2
                    print("Used a middle piont for relief line")

                relates_to = depths_adjusted_dict[adjusted_depth][index_to_use]
                potential_line.append(SimplePoint(relates_to.get_x(),relates_to.get_y(),relates_to))
        if len(potential_line) > 1:
            relief_lines[adjusted_depth] = potential_line

    #Step 4
    # Extra points, the yellow buoy dive1-line-3 has a sphere plastic cement filled anchor at reel point 210
    # From there we hooked a reel to it and surface swam to the buoy. We then took a back bearing of 325 degrees (opposite: 145 degrees)
    # And distance reading of 192 ft and depth of 41 feet top 42 feet bottom
    # knowing dive1-line3 point we can use it as reference point to find coordinates for the buoy anchor point.
    # buoy dive 10:00 on 7 Nov was 10 ft tide.
    points_of_interest = []
    buoy_ref_line = get_dive_line_by_name(dive_lines,"dive1-line3")
    if buoy_ref_line is None:
            print("PROBLEM getting ref line")
    buoy_ref_point = buoy_ref_line.get_point_by_reel_length_mark_ft(210)
    if buoy_ref_point is None:
        print("PROBLEM getting ref point")
    buoy_point = DivePointInterest('yellow-buoy', buoy_ref_point, 42, "7-11-2020", "10:00", 10, buoy_ref_point.get_tide_height_target_ft(), 145, buoy_ref_point.get_magnetic_declination_deg(), 192, 'Closest yellow buoy')
    points_of_interest.append(buoy_point)


    # Step 5, write data to file
    for dive_line in dive_lines:
        #ppRowDict(dive_line)
        #write_line_to_shape_file(new_dir,dive_line)
        write_line_to_geojson_file(new_dir,dive_line)

    for name, points in point_sets.items():
       # write_points_to_shape_file(new_dir,name + '-points',points)
        write_points_to_geojson_file(new_dir,name + '-points',points)

    # Write points of interest
    write_points_to_geojson_file(new_dir,'points-of-interest',points_of_interest)

    # Step 4.x write relief lines to file
    for adjusted_depth, relief_line in relief_lines.items():
        #write_points_to_shape_file(new_dir,'relief_line_{}'.format(str(adjusted_depth).replace(".", "_")),relief_line)
        coords = to_coord_list(relief_line)
        sorted_coords = sorted(coords,key=itemgetter(1)) #This sorts coordinates north to south
        #write_relief_line_to_shape_file(new_dir,'relief_line_{}'.format(str(adjusted_depth).replace(".", "_")),to_relief_line_dict(sorted_coords,adjusted_depth))
        write_relief_line_to_geojson_file(new_dir,'relief_line_{}'.format(str(adjusted_depth).replace(".", "_")),to_relief_line_dict(sorted_coords,adjusted_depth))

def get_dive_line_by_name(dive_lines,name):
    line_to_return = None
    for line in dive_lines:
        if line.get_name() == name:
            line_to_return = line
            break
    return line_to_return

### Sort unique function
def sort_uniq(sequence):
    return map(
        operator.itemgetter(0),
        itertools.groupby(sorted(sequence)))

### Helper function to add points
def add_to_points_by_adjusted_depth(points_by_adjusted_depth, adjusted_depth, point):
    if adjusted_depth in points_by_adjusted_depth:
        points_by_adjusted_depth[adjusted_depth].append(point)
    else:
        arr = []
        arr.append(point)
        points_by_adjusted_depth[adjusted_depth]=arr

### Helper function to get reel length mark between 2 dive points
def get_reel_length_mark_ft_between_2_points(dive_point_1, dive_point_2):
    return dive_point_1.get_reel_length_mark_ft() + \
      ((dive_point_2.get_reel_length_mark_ft()-dive_point_1.get_reel_length_mark_ft())/2)


### Helper function to get reel length mark between 2 dive points
def get_depth_reading_ft_between_2_points(dive_point_1, dive_point_2):
    if dive_point_2.get_depth_reading_ft() > dive_point_1.get_depth_reading_ft():
        return dive_point_1.get_depth_reading_ft() + \
            ((dive_point_2.get_depth_reading_ft()-dive_point_1.get_depth_reading_ft())/2)
    elif dive_point_2.get_depth_reading_ft() < dive_point_1.get_depth_reading_ft():
        return dive_point_2.get_depth_reading_ft() + \
                    ((dive_point_1.get_depth_reading_ft()-dive_point_2.get_depth_reading_ft())/2)
    else:
        return dive_point_1.get_depth_reading_ft()


###
def to_coord_list(simple_point_list):
        return list(map(lambda point: point.to_long_lat(),simple_point_list))

def to_relief_line_dict(coord_list, depth):
        return {
            'geometry' :
                {
                    'type':'LineString',
                    'coordinates': coord_list
                },
            'properties':
                {
                    'depthAdjustedFt': depth
                },
            }
### Helper debug function
def pp_dive_line(dive_line):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(dive_line.to_line_row_dict())

### Writing to shapefile functions
def write_line_to_shape_file(dirLoc,dive_line):
    file_path = os.path.abspath(os.path.join(dirLoc,dive_line.get_name() + '.shp'))
    lineShp = fiona.open(file_path, mode='w', driver='ESRI Shapefile', schema = dive_line.get_schema(), crs = "EPSG:4326")
    lineShp.write(dive_line.to_line_row_dict())
    lineShp.close()

def write_line_to_geojson_file(dirLoc,dive_line):
    file_path = os.path.abspath(os.path.join(dirLoc,dive_line.get_name() + '.geojson'))
    lineShp = fiona.open(file_path, mode='w', driver='GeoJSON', schema = dive_line.get_schema(), crs = "EPSG:4326")
    lineShp.write(dive_line.to_line_row_dict())
    lineShp.close()


def write_points_to_shape_file(dirLoc,name,points):
    file_path = os.path.abspath(os.path.join(dirLoc,name + '.shp'))
    lineShp = fiona.open(file_path, mode='w', driver='ESRI Shapefile', schema = points[0].get_schema(), crs = "EPSG:4326")
    for point in points:
        lineShp.write(point.to_point_row_dict())
    lineShp.close()

def write_points_to_geojson_file(dirLoc,name,points):
    file_path = os.path.abspath(os.path.join(dirLoc,name + '.geojson'))
    lineShp = fiona.open(file_path, mode='w', driver='GeoJSON', schema = points[0].get_schema(), crs = "EPSG:4326")
    for point in points:
        lineShp.write(point.to_point_row_dict())
    lineShp.close()

def write_relief_line_to_shape_file(dirLoc,name,to_relief_line_dict):
    file_path = os.path.abspath(os.path.join(dirLoc,name + '.shp'))
    lineShp = fiona.open(file_path, mode='w', driver='ESRI Shapefile', schema = schemas.relief_line, crs = "EPSG:4326")
    lineShp.write(to_relief_line_dict)
    lineShp.close()

def write_relief_line_to_geojson_file(dirLoc,name,to_relief_line_dict):
    file_path = os.path.abspath(os.path.join(dirLoc,name + '.geojson'))
    lineShp = fiona.open(file_path, mode='w', driver='GeoJSON', schema = schemas.relief_line, crs = "EPSG:4326")
    lineShp.write(to_relief_line_dict)
    lineShp.close()


### System helper functions
def create_or_empty(dir_location):
    if not dir_location.exists():
        dir_location.mkdir()
    else:
        empty_dir(dir_location)

def empty_dir(dir_location):
    if not bool(list(dir_location.rglob('*'))):
        for root, dirs, files in os.walk(dir_location):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

if __name__ == "__main__":
    main()
