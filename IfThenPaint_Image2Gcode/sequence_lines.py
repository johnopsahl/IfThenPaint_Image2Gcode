import numpy as np
import math

def sequence_lines(stroke_lines, 
                   image_pixel_width, 
                   image_pixel_height, 
                   section_side_length):
    # a next cloest line algorithm, used to optimize the order in which strokes
    # are painted to minimize the amount of time required to paint
    
    number_of_lines = len(stroke_lines)
    
    sequence_stroke_lines = []
    
    #initialize 2d sections_points array
    section_points = []
    
    row_count = round(image_pixel_height/section_side_length)
    column_count = round(image_pixel_width/section_side_length)
    
    for i in range(row_count):
        section_points.append([])
        for j in range(column_count):
            section_points[i].append([])
    
    # log stroke lines by section
    for i in range(len(stroke_lines)):
        
        start_point = stroke_lines[i][0]
        end_point = stroke_lines[i][1]
        
        # log by start point
        section_row = math.floor(stroke_lines[i][0][1]/section_side_length)
        section_column = math.floor(stroke_lines[i][0][0]/section_side_length)
        section_points[section_row][section_column].append([start_point, end_point])
        
        # log by end point
        section_row = math.floor(stroke_lines[i][1][1]/section_side_length)
        section_column = math.floor(stroke_lines[i][1][0]/section_side_length)
        section_points[section_row][section_column].append([end_point, start_point])
    
    # first stroke line as the first line in the stroke_lines array
    start_point = stroke_lines[0][0]
    end_point = stroke_lines[0][1]
    
    sequence_stroke_lines.append([[start_point[0], start_point[1]],
                                  [end_point[0], end_point[1]]])
    
    # position of line start point entry in section_points
    start_row, \
    start_column, \
    start_index = position_in_section_points(start_point,
                                             end_point,
                                             section_points, 
                                             section_side_length)
    
    # delete end point instances of stroke from section_points array
    del section_points[start_row][start_column][start_index]
    
    # position of line end point entry in section_points
    end_row, \
    end_column, \
    end_index = position_in_section_points(end_point,
                                           start_point,
                                           section_points, 
                                           section_side_length)
    
    current_point = end_point
    
    # delete end point instances of stroke from section_points array
    del section_points[end_row][end_column][end_index]

    # determine next closest point by evaluation of points in next closest section(s)
    search_center = [end_row, end_column]
    
    line_count = 1
    
    while line_count < number_of_lines:
        
        next_point_found = False
        search_outside_bounds = False
        search_level = 0
        distance_compare = 999999999
       
        # do not this while loop if all points have been found
        while next_point_found == False and search_outside_bounds == False:
            
            row_low = search_center[0] - search_level
            row_high = search_center[0] + search_level
            column_low = search_center[1] - search_level
            column_high = search_center[1] + search_level
            
            # if all search limits are outside the bounds of the search sections
            if row_low < 0 and \
               row_high > row_count - 1 and \
               column_low < 0 and \
               column_high > column_count - 1:
                  search_outside_bounds = True
            
            # limit search bounds to size of search sections
            row_low = if_less_than_set_equal_to(row_low, 0)
            row_high = if_greater_than_set_equal_to(row_high, row_count - 1)
            column_low = if_less_than_set_equal_to(column_low, 0)
            column_high = if_greater_than_set_equal_to(column_high, column_count - 1)
                                  
            for row in range(row_low, row_high + 1):
                for column in range(column_low, column_high + 1):
                    
                   # limit search to only the sections that have not been searched yet
                   # i.e. don't search internal sections, just sections at the new search level
                   if row == search_center[0] - search_level or \
                      row  == search_center[0] + search_level or \
                      column == search_center[1] - search_level or \
                      column == search_center[1] + search_level:

                          for index in range(len(section_points[row][column])):
                              
                              x_temp = section_points[row][column][index][0][0]
                              y_temp = section_points[row][column][index][0][1]
                              
                              distance_temp = comparitive_distance(current_point[0],
                                                                   current_point[1],
                                                                   x_temp,
                                                                   y_temp)
                              
                              if distance_temp < distance_compare:
                                  distance_compare = distance_temp
                                  next_point_found == True
                                  next_row = row
                                  next_column = column
                                  next_index = index
            
            # advance to next search level                  
            search_level += 1
        
        start_point = section_points[next_row][next_column][next_index][0]
        end_point = section_points[next_row][next_column][next_index][1]
        
        sequence_stroke_lines.append([start_point, end_point])
        
        # delete start point instance of stroke from section_points array
        del section_points[next_row][next_column][next_index]
        
        # position of line end point entry in section_points
        end_row, \
        end_column, \
        end_index = position_in_section_points(end_point,
                                               start_point,
                                               section_points, 
                                               section_side_length)
        
        current_point = end_point
        
        # delete end point instances of stroke from section_points array
        del section_points[end_row][end_column][end_index]
        
        line_count += 1
    
    sequence_stroke_lines = np.asarray(sequence_stroke_lines)
    
    return sequence_stroke_lines

def if_less_than_set_equal_to(val, lower_limit):
    
    if val < lower_limit:
        return lower_limit
    return val

def if_greater_than_set_equal_to(val, upper_limit):
    
    if val > upper_limit:
        return upper_limit
    return val
        
def comparitive_distance(x1, y1, x2, y2):
    
    distance = (x2 - x1)**2 + (y2 - y1)**2
    
    return distance

def position_in_section_points(ref_point1, ref_point2, 
                               section_points, section_side_length):
    
    row = math.floor(ref_point1[1]/section_side_length)
    column = math.floor(ref_point1[0]/section_side_length)
    
    # determine position of line in section_points array
    for i in range(len(section_points[row][column])):
        if section_points[row][column][i][0][0] == ref_point1[0] and \
           section_points[row][column][i][0][1] == ref_point1[1] and \
           section_points[row][column][i][1][0] == ref_point2[0] and \
           section_points[row][column][i][1][1] == ref_point2[1] :
            index = i
    
    return row, column, index