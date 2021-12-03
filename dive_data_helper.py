# Simple lookup to find dive
def lookup_dive(dive_data, dive_num):
    current_dive = None
    for dive in dive_data['dives']:
        if dive["number"] == dive_num:
            current_dive = dive
    return current_dive

# Simple lookup to find dive and line
def lookup_dive_line(dive_data, dive_num, line_num):
    current_dive = None
    current_line = None
    for dive in dive_data['dives']:
        if dive["number"] == dive_num:
            current_dive = dive
            for line in dive["lines"]:
                if line["number"] == line_num:
                    current_line = line
    return (current_dive, current_line)

# Simple lookup to find dive line and point
# no need to optimize.. 2 dives, 3 lines per dive and at most 30 points per line
def lookup_dive_line_point(dive_data, dive_num, line_num, point_mrk_ft):
    current_dive = None
    current_line = None
    current_point = None

    for dive in dive_data['dives']:
        if dive["number"] == dive_num:
            current_dive = dive
            for line in dive["lines"]:
                if line["number"] == line_num:
                    current_line = line
                    for point in line["points"]:
                        if point_mrk_ft == point['reelLengthMarkFt']:
                            current_point = point
                            break

    return (current_dive, current_line, current_point)