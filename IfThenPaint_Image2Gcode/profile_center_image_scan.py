import math
import numpy as np
import geometry as geom
    
def profile_centers_from_image(image_width,
                               image_height,
                               scan_angle, 
                               profile_width, 
                               profile_length, 
                               scan_line_offset_overlap,
                               scan_line_increment_overlap):
    
    center = [image_width/2, image_height/2]
    
    scan_line_offset = profile_width*(1 - scan_line_offset_overlap)
    scan_line_increment = profile_length*(1 - scan_line_increment_overlap)
    
    if scan_angle == 0: #horiztonal line
        x_scan_increment = scan_line_increment
        y_scan_increment = 0
    elif scan_angle == math.pi/2: #verticlal line
        x_scan_increment = 0
        y_scan_increment = scan_line_increment
    else:
        x_scan_increment = scan_line_increment*math.cos(scan_angle)
        y_scan_increment = scan_line_increment*math.sin(scan_angle)
        
    scan_slope = math.tan(scan_angle)
    scan_line_offset_coeff = (1 + scan_slope**2)**0.5
    scan_intercept = center[1] - scan_slope * center[0]
    
    image_scan = 'incomplete'
    scan_line_offset_direction = 'positive'
    profile_center = []
    last_profile_in_scan_line = []
    
    while image_scan == 'incomplete':
        
        # calculate where scan line intersects sides of the images perimeter
        if scan_angle == 0: # horizointal line              
            scan_start = [0, center[1]]
            scan_end = [image_width, center[1]]
        elif scan_angle == math.pi/2: # vertical line
            scan_start = [center[0], 0]
            scan_end = [center[0], image_height]
        else: # all other line slopes
            scan_start, scan_end = scan_line_start_and_end(scan_slope, 
                                                           scan_intercept, 
                                                           0, 
                                                           image_width, 
                                                           0, 
                                                           image_height)
                  
        # total length of scan
        scan_length = geom.distance_2d(scan_start[0],
                                       scan_start[1],
                                       scan_end[0],
                                       scan_end[1])
        
        # set profile center as start of scan
        center[0] = scan_start[0]
        center[1] = scan_start[1]
               
        scan_distance = 0
        
        while scan_distance < scan_length:
            
            #log profile center
            profile_center.append([center[0], center[1]]) 
            
            # advance profile center by scan increment
            center[0] += x_scan_increment
            center[1] += y_scan_increment
                    
            scan_distance += scan_line_increment
            
        # record the index of the last profile center in the scan line
        last_profile_in_scan_line.append(len(profile_center) - 1)     
                
        # advance to next line
        if scan_line_offset_direction == 'positive':

            if scan_angle == 0: # horiztonal line
                center[1] += scan_line_offset
            elif scan_angle == math.pi/2: # vertical line
                center[0] += scan_line_offset
            else:
                scan_intercept += scan_line_offset*scan_line_offset_coeff
                
        elif scan_line_offset_direction == 'negative':
            
            if scan_angle == 0: # horizontal line
                center[1] -= scan_line_offset
            elif scan_angle == math.pi/2: # vertical line
                center[0] -= scan_line_offset
            else:
                scan_intercept -= scan_line_offset*scan_line_offset_coeff
        
        line_location = line_outside_rectangle(center, 
                                               scan_slope, 
                                               scan_intercept, 
                                               0, 
                                               image_width, 
                                               0, 
                                               image_height)
        
        #if line above image area
        if line_location == 'vert_right' or \
           line_location == 'horiz_above' or \
           line_location == 'pos_above' or \
           line_location == 'neg_above':
            
            scan_line_offset_direction = 'negative'
            center = [image_width/2, image_height/2]
            scan_intercept = center[1] - scan_slope*center[0]
            
            if scan_angle == 0: # horiztonal line
                center[1] -= scan_line_offset
            elif scan_angle == math.pi/2: # vertical line
                center[0] -= scan_line_offset
            else:
                scan_intercept -= scan_line_offset*scan_line_offset_coeff
                
        #if line below image area
        elif line_location == 'vert_left' or \
             line_location == 'horiz_below' or \
             line_location == 'pos_below' or \
             line_location == 'neg_below':
                image_scan = 'complete'
                
    profile_center = np.asarray(profile_center)
    last_profile_in_scan_line = np.asarray(last_profile_in_scan_line)
    
    return profile_center, last_profile_in_scan_line

def scan_line_start_and_end(slope, intercept, 
                            x_left, x_right, y_bottom, y_top):
    #calculate start and end position of scan for slope != 90 or slope != 0
	
    y_left = x_left*slope + intercept
    y_right = x_right*slope + intercept
    
    start = [0, 0]
    end = [0, 0]
    temp = [0, 0]
    
    if y_left >= y_bottom:
        if y_left <= y_top:
            start[0] = x_left
            start[1] = y_left
        else: # y_left > height
            start[1] = y_top
            start[0] = (y_top - intercept)/slope
    else: # y_left < 0
        start[1] = y_bottom
        start[0] = (y_bottom - intercept)/slope

    if y_right >= y_bottom:
        if y_right <= y_top:
            end[0] = x_right
            end[1] = y_right
        else: # y_right > height
            end[1] = y_top
            end[0] = (y_top - intercept)/slope
    else: # y_right < 0
        end[1] = y_bottom
        end[0] = (y_bottom - intercept)/slope
    
    # start at right most point for negative slopes
    if slope < 0:
        temp = start
        start = end
        end = temp
        
    return start, end

def line_outside_rectangle(line_point, slope, intercept, 
                           x_left, x_right, y_bottom, y_top):
    
    y_left = x_left*slope + intercept
    y_right = x_right*slope + intercept
    
    line_location = "inside"
    
    if 0 <= slope < 0.0001: # horiztontal line
        if line_point[1] > y_top:
            line_location = 'horiz_above'
        if line_point[1] < y_bottom:
            line_location = 'horiz_below'
    elif slope > 1000: # vertical line
        if line_point[0] > x_right:
            line_location = 'vert_right'
        elif line_point[0] < x_left:
            line_location = 'vert_left'
    elif slope > 0:
        if y_left > y_top:
            line_location = 'pos_above'
        elif y_right < y_bottom:
            line_location = 'pos_below'
    elif slope < 0:
        if y_right > y_top:
            line_location = 'neg_above'
        elif y_left < y_bottom:
            line_location = 'neg_below'
    
    return line_location