from collections import OrderedDict
# Naming convention for line: dive#-line#
# Naming convention for point: dive#-line#-pt#
## example: dive2-line3-pt150 = The 150 ft marking point taken off the 3rd line on the second dive
dive_line = {
'geometry':'LineString',
'properties': OrderedDict([
      ('name', 'str'),
      ('diveNumber', 'int'),
      ('lineNumber', 'int'),
      ('date', 'str'),
      ('time', 'str'),
      ('lengthFt', 'int'),
      ('distanceToRefPtFt', 'int'),
      ('lengthAdjustedFt', 'int'),
      ('headingDeg', 'int'),
      ('magneticDeclinationDeg', 'int'),
      ('headingAdjustedDeg', 'int'),
      ('tideHeightFt', 'float'),
      ('pointDepthAdjustmentFt', 'int'),
      ('tideHeightTargetFt', 'float'),
      ('refPointUTMEasting19T', 'float'),
      ('refPointUTMNorthing19T', 'float')
    ])
}

dive_line_point = {
'geometry':'Point',
'properties': OrderedDict([
      ('name', 'str'),
      ('diveNumber', 'int'),
      ('lineNumber', 'int'),
      ('date', 'str'),
      ('lineTime', 'str'),
      ('tideHeightFt', 'float'),
      ('tideHeightTargetFt', 'float'),
      ('pointDepthAdjustmentFt', 'int'),
      ('depthReadingFt', 'float'),
      ('depthAdjustedFt', 'float'),
      ('reelLengthMarkFt', 'int'),
      ('distanceToRefPtFt', 'int'),
      ('lineHeadingDeg', 'int'),
      ('magneticDeclinationDeg', 'int'),
      ('lineHeadingAdjustedDeg', 'int'),
      ('refPointUTMEasting19T', 'float'),
      ('refPointUTMNorthing19T', 'float'),
      ('isExtrapolated', 'str')
    ])
}

dive_point_of_interest = {
'geometry':'Point',
'properties': OrderedDict([
      ('name', 'str'),
      ('date', 'str'),
      ('time', 'str'),
      ('tideHeightFt', 'float'),
      ('tideHeightTargetFt', 'float'),
      ('pointDepthAdjustmentFt', 'int'),
      ('depthReadingFt', 'float'),
      ('depthAdjustedFt', 'float'),
      ('distanceToRefPtFt', 'int'),
      ('lineHeadingDeg', 'int'),
      ('magneticDeclinationDeg', 'int'),
      ('lineHeadingAdjustedDeg', 'int'),
      ('refPointUTMEasting19T', 'float'),
      ('refPointUTMNorthing19T', 'float'),
      ('description', 'str')
    ])
}


simple_point = {
'geometry':'Point',
'properties': OrderedDict([
      ('depthAdjustedFt', 'float')
    ])
}

relief_line = {
'geometry':'LineString',
'properties': OrderedDict([
      ('depthAdjustedFt', 'float')
    ])
}
