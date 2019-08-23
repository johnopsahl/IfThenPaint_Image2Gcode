import numpy as np
import math

def atan3(dy, dx): 
    # tangent function that recognizes positive and negative angles

    # rounding error causes some small negative numbers that should be zero
    # then tan3 function interprets as close to 2*pi instead of close to zero
    # set all small negative dy values equal to zero
    if -1e-15 < dy < 0.0:
        dy = 0.0

    angle = math.atan2(dy, dx)
    if angle < 0:
        angle += 2 * math.pi
        
    return angle

def line_segment_center(x1, y1, x2, y2):
    # center of a line segment
    # inputs must be numpy arrays
    
    x_center = (x1 + x2)/2
    y_center = (y1 + y2)/2

    center = np.stack([x_center, y_center], axis = 1)
    
    return center

def distance_2d(x1, y1, x2, y2):
    # distance between two points
    
    distance = ((x2 - x1)**2 + (y2 - y1)**2)**0.5

    return distance

def distance_3d(x1, y1, z1, x2, y2, z2):
    # distance between two points
    
    distance = ((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)**0.5

    return distance

def lines_intersect(line1_start, line1_end, line2_start, line2_end):
    # determine if two lines intersect
    
    # https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
        
    orientation1 = line_and_point_orientation(line1_start, line1_end, line2_start)
    orientation2 = line_and_point_orientation(line1_start, line1_end, line2_end)
    orientation3 = line_and_point_orientation(line2_start, line2_end, line1_start)
    orientation4 = line_and_point_orientation(line2_start, line2_end, line1_end)
    
    if (orientation1 != orientation2 and orientation3 != orientation4) or \
       (orientation1 == 0 and point_on_line_segment(line2_start, line1_start, line1_end)) or \
       (orientation1 == 0 and point_on_line_segment(line2_end, line1_start, line1_end)) or \
       (orientation1 == 0 and point_on_line_segment(line1_start, line2_start, line2_end)) or \
       (orientation1 == 0 and point_on_line_segment(line1_end, line2_start, line2_end)):
           return True

    return False
    
def line_and_point_orientation(line_start, line_end, point):
    
    #line_start is point 1
    #line_end is point 2
    #point is point 3
    
    #slope of line between point 1 and point 2, tau = (y2-y1)/(x2-x1)
    #slope of line between point 2 and point 3, sigma = (y3-y2)/(x3-x2)
    
    #if sigma < tau, ccw -> left turn
    #if sigma = tau, collinear
    #if sigma > tau, ccw -> right turn
    
    #sigma - tau = (y2-y1)*(x3-x2)-(y3-y2)*(x2-x1)
    
    val = (line_end[1] - line_start[1])*(point[0] - line_end[0]) \
          - (point[1] - line_end[1])*(line_end[0] - line_start[0])
    
    if val > 0:
        orientation = 1 #cw
    elif val < 0:
        orientation = 2 #ccw
    else: #area == 0
        orientation = 0 # colinear
    
    return orientation

def point_inside_rectangle(x_coord, y_coord, corners):
    # determine if a point exists inside a rectangle
    
    AB = corners[1] - corners[0]
    AM = np.asarray([x_coord - corners[0][0], y_coord - corners[0][1]])
    BC = corners[2] - corners[1]
    BM = np.asarray([x_coord - corners[1][0], y_coord - corners[1][1]])
    
    if 0 <= np.dot(AB, AM) <= np.dot(AB, AB) and \
       0 <= np.dot(BC, BM) <= np.dot(BC, BC):
        return True
    else:
        return False
    
def point_on_line_segment(point, line_start, line_end):
    # check if point is on a line segment
    
    if point[0] <= max(line_start[0], line_end[0]) and \
       point[0] >= min(line_start[0], line_end[0]) and \
       point[1] <= max(line_start[1], line_end[1]) and \
       point[1] >= min(line_start[1], line_end[1]):
        return True
    
    return False

def rotate_vector_about_origin(vector, angle):
    #rotate vectors by angle about the origin (0,0)
    #inputs must be numpy arrays
    
    x_temp, y_temp = np.squeeze(np.split(vector, 2, axis = 1))
    
    x_coord = x_temp*np.cos(angle) - y_temp*np.sin(angle)
    y_coord = x_temp*np.sin(angle) + y_temp*np.cos(angle)
    
    vector_rotated = np.stack([x_coord, y_coord], axis = 1)
        
    return vector_rotated

def sorted_lines_and_corners(line, profile_width, profile_length):
    
    # get coordinate arrays from line array
    start, end = np.squeeze(np.hsplit(line, 2))
    x_start, y_start = np.squeeze(np.hsplit(start, 2))
    x_end, y_end = np.squeeze(np.hsplit(end, 2))
    
    if len(line) == 1:
        x_start = np.asarray([x_start])
        y_start = np.asarray([y_start])
        x_end = np.asarray([x_end])
        y_end = np.asarray([y_end])
    
    length = distance_2d(x_start, y_start, x_end, y_end)
    angle = np.arctan2(y_end - y_start, x_end - x_start)
    center = line_segment_center(x_start, y_start, x_end, y_end)
    
    indices = (-length).argsort()
    
    length_sorted = length[indices]
    angle_sorted = angle[indices]
    
    line_sorted = line[indices]
    center_sorted = center[indices]
    
    # calculate corners of profile centered at (0,0) and scan angle 0 deg   
    corner_offset = np.asarray([[profile_length/2,   profile_width/2],   
                                [-profile_length/2,  profile_width/2],
                                [-profile_length/2, -profile_width/2],
                                [ profile_length/2, -profile_width/2]])
    
    length_offset = np.stack([length_sorted/2, np.zeros(len(length_sorted))], axis = 1)
    
    corner_1_offset =  length_offset + corner_offset[0]
    corner_2_offset = -length_offset + corner_offset[1]
    corner_3_offset = -length_offset + corner_offset[2]
    corner_4_offset =  length_offset + corner_offset[3]
    
    # rotate corner vectors about (0,0) by the scan angle   
    corner_1_offset = rotate_vector_about_origin(corner_1_offset, angle_sorted)
    corner_2_offset = rotate_vector_about_origin(corner_2_offset, angle_sorted)
    corner_3_offset = rotate_vector_about_origin(corner_3_offset, angle_sorted)
    corner_4_offset = rotate_vector_about_origin(corner_4_offset, angle_sorted)
    
    # calculate profile corners
    corner_1 = corner_1_offset + center_sorted
    corner_2 = corner_2_offset + center_sorted
    corner_3 = corner_3_offset + center_sorted
    corner_4 = corner_4_offset + center_sorted
      
    corner_sorted = np.stack([corner_1, corner_2, corner_3, corner_4], axis = 1)
    
    return line_sorted, corner_sorted

def length_of_line(line):
    
    #get length of each selected line
    start, end = np.squeeze(np.hsplit(line, 2))
    x_start, y_start = np.squeeze(np.hsplit(start, 2))
    x_end, y_end = np.squeeze(np.hsplit(end, 2))
    
    if len(line) == 1:
        x_start = np.asarray([x_start])
        y_start = np.asarray([y_start])
        x_end = np.asarray([x_end])
        y_end = np.asarray([y_end])
    
    length = distance_2d(x_start, y_start, x_end, y_end)
    
    return length