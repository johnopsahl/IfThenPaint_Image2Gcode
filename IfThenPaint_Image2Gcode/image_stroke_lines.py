import math
import numpy as np
import geometry as geom
import profile_center_image_scan as pcis

def stroke_lines_from_image(color_mask,
                            scan_color,
                            scan_angle, 
                            profile_width, 
                            profile_length,
                            color_match_threshold,
                            scan_line_offset_overlap,
                            scan_line_increment_overlap):
    
    image_height, image_width = color_mask.shape[:2]
    scan_angle = math.radians(scan_angle)
    
    # generate list of profile centers from image
    profile_center, \
    last_profile_in_scan_line = pcis.profile_centers_from_image(image_width,
                                                                image_height,
                                                                scan_angle, 
                                                                profile_width, 
                                                                profile_length, 
                                                                scan_line_offset_overlap,
                                                                scan_line_increment_overlap)
    
    # calculate corners of profile centered at (0,0) and scan angle 0 deg
    corner_offset = np.asarray([[ profile_length/2,  profile_width/2],
                                [-profile_length/2,  profile_width/2],
                                [-profile_length/2, -profile_width/2],
                                [profile_length/2, -profile_width/2]])
    
    corner_offset = geom.rotate_vector_about_origin(corner_offset, scan_angle)
    
    # calculate profile corners
    corner_1 = profile_center + corner_offset[0]
    corner_2 = profile_center + corner_offset[1]
    corner_3 = profile_center + corner_offset[2]
    corner_4 = profile_center + corner_offset[3]
    
    # check if corners are inside of image
    corner_1_inside = [0 <= x[0] < image_width and 0 <= x[1] < image_height for x in corner_1]
    corner_2_inside = [0 <= x[0] < image_width and 0 <= x[1] < image_height for x in corner_2]
    corner_3_inside = [0 <= x[0] < image_width and 0 <= x[1] < image_height for x in corner_3]
    corner_4_inside = [0 <= x[0] < image_width and 0 <= x[1] < image_height for x in corner_4]
    
    profile_inside = np.logical_and(np.logical_and(corner_1_inside, 
                                                   corner_2_inside), 
                                    np.logical_and(corner_3_inside, 
                                                   corner_4_inside))
       
    # create new profile centers array that excludes profile centers that are outside the image
    profile_inside_index = np.where(profile_inside == True)
    profile_inside_index = profile_inside_index[0]
    
    profile_center = profile_center[profile_inside_index]
    profile_center_index = profile_inside_index
    corner_1 = corner_1[profile_inside_index]
    corner_2 = corner_2[profile_inside_index]
    corner_3 = corner_3[profile_inside_index]
    corner_4 = corner_4[profile_inside_index]
    
    corner_low, corner_high = scan_corners(corner_offset)
    
    # determine pixel scan range; results is (x range, y range)
    pixel_scan_range = np.uint16(np.ceil(corner_high) - np.floor(corner_low))
#    pixel_scan_range = np.uint16(corner_high - corner_low)

    # set pixel_eval to location of the first pixel
    pixel_eval_first = np.uint16(profile_center + corner_low)
    
    # determine if pixel is inside the profile
    AB = corner_2 - corner_1
    BC = corner_3 - corner_2
    
    profile_pixel_count = np.zeros(len(profile_center))
    
    for i in range(pixel_scan_range[0]): # add one for rounding error
        
        for j in range(pixel_scan_range[1]): # add one for rounding error
            
            # advance to next pixel
            pixel_eval = pixel_eval_first + np.asarray([i, j])
            
            # determine if pixel inside profile
            AM = pixel_eval - corner_1
            BM = pixel_eval - corner_2
            
            dot_AB_AM = np.multiply(AB, AM).sum(1)
            dot_AB_AB = np.multiply(AB, AB).sum(1)
            dot_BC_BM = np.multiply(BC, BM).sum(1)
            dot_BC_BC = np.multiply(BC, BC).sum(1)
            
            inside_check_1 = np.asarray([0 <= x <= y for x, y in zip(dot_AB_AM, dot_AB_AB)])
            inside_check_2 = np.asarray([0 <= x <= y for x, y in zip(dot_BC_BM, dot_BC_BC)])
            inside_profile = np.logical_and(inside_check_1, inside_check_2)
            
            # determine if pixel inside profile matches the scan color
            color_match = [x == True and color_mask[(image_height - 1) - y[1]][y[0]] == 255 for x, y in zip(inside_profile, pixel_eval)]
            
            # add count to array if pixel is both inside profile and matches color
            profile_pixel_count += color_match

    # average number of pixels in each brush profile
    avg_profile_pixels = int(profile_width*profile_length)
    
    # profile valid if a certain percentage of pixels inside profile match the scan color
    profile_valid = np.asarray([x/avg_profile_pixels >= color_match_threshold for x in profile_pixel_count])
    
    # reduce profile centers array to valid profiles only
    profile_valid_index = np.where(profile_valid == True)
    
    profile_center = profile_center[profile_valid_index]
    profile_center_index = profile_center_index[profile_valid_index]
    
    # group profile center indices by scan line, this could be more efficient
    scan_line_profile_index = [[] for x in last_profile_in_scan_line]
    
    for i in range(len(last_profile_in_scan_line)):
        
        if i == 0:
            first_profile_index = -1
        else:
            first_profile_index = last_profile_in_scan_line[i - 1]
            
        for j in range(len(profile_center_index)):
            if first_profile_index < profile_center_index[j] <= last_profile_in_scan_line[i]:
                scan_line_profile_index[i].append(j)
    
    scan_line_profile_index = np.asarray(scan_line_profile_index)
    
    # determine stroke lines, could be more efficient
    stroke_line = []
         
    for i in range(len(scan_line_profile_index)):
        
        if len(scan_line_profile_index[i]) != 0:
            
            first_profile_in_scan_line = True
            
            for j in range(len(scan_line_profile_index[i])):
            
                if first_profile_in_scan_line == True:
                    start = profile_center[scan_line_profile_index[i][j]]
                    end = profile_center[scan_line_profile_index[i][j]] + \
                          0.001*np.asarray([np.cos(scan_angle), np.sin(scan_angle)])
                    first_profile_in_scan_line = False
                elif (profile_center_index[scan_line_profile_index[i][j]] - \
                      profile_center_index[scan_line_profile_index[i][j - 1]]) == 1:
                    end = profile_center[scan_line_profile_index[i][j]]
                else:
                    stroke_line.append([[start[0], start[1]], [end[0], end[1]]])
                    start = profile_center[scan_line_profile_index[i][j]]
                    end = profile_center[scan_line_profile_index[i][j]] + \
                          0.001*np.asarray([np.cos(scan_angle), np.sin(scan_angle)])
                
                # if last profile in scan line
                if j == (len(scan_line_profile_index[i]) - 1):
                    stroke_line.append([[start[0], start[1]], [end[0], end[1]]])
    
#    stroke_line = np.asarray(stroke_line)
    
    return stroke_line

def scan_corners(points): 
    # determine min and max x and y of a set of points
   
    x = [x[0] for x in points]
    y = [x[1] for x in points]
    
    corner_low = np.asarray([min(x), min(y)])
    corner_high = np.asarray([max(x), max(y)])
    
    return corner_low, corner_high