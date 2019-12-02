#import cProfile
#from matplotlib import pyplot as plt
#from matplotlib.collections import LineCollection

import os
import cv2
import time
import json
import numpy as np
import image_processing as imgproc
import geometry as geom
import image_stroke_lines as imgstrln
import line_max_length as lnmaxlen
import select_lines as selctln
import sequence_lines as sqnlns
from definitions import DATA_PATH

# the parameters used by the line scan function to generate paint strokes from
# a digital image by paint color
scan_1 = {'name': 'process_2',
          'scan_color_bgr': [158, 158, 158],
          'scan_angle_start': 0,
          'scan_angle_increment': 90,
          'scan_angle_end': 180,
          'profile_width': 6,
          'profile_length': 6,
          'color_match_threshold': 0.4,
          'scan_line_offset_overlap': 0.1,
          'scan_line_increment_overlap': 0.1,
          'select_line_width_overlap': 0.001,
          'select_line_length_overlap': 0,
          'select_line_min_length': 0,
          'stroke_line_max_length': 10}

scan_2 = {'name': 'line_scan_green',
          'scan_color_bgr': [23, 41, 35],
          'scan_angle_start': 0,
          'scan_angle_increment': 90,
          'scan_angle_end': 180,
          'profile_width': 3,
          'profile_length': 3,
          'color_match_threshold': 0.4,
          'scan_line_offset_overlap': 0,
          'scan_line_increment_overlap': 0.1,
          'select_line_width_overlap': 0.001,
          'select_line_length_overlap': 0,
          'select_line_min_length': 0,
          'stroke_line_max_length': 150}

def line_scan(scan, image_prop, null_color):
    # generates paint stroke lines from a bitmap image by paint color
    
    image_quant = cv2.imread(os.path.join(DATA_PATH, 'image_quant.png'))
    image_eval = image_quant.copy()
    
    scan_color = np.asarray(scan['scan_color_bgr'])
    
    # convert length values to pixels
    profile_width = scan['profile_width']*image_prop['pixel_per_mm']
    profile_length = scan['profile_length']*image_prop['pixel_per_mm']
    select_line_min_length = scan['select_line_min_length']*image_prop['pixel_per_mm']
    stroke_line_max_length = scan['stroke_line_max_length']*image_prop['pixel_per_mm']
    
    line_found = True
    line_selected = True
    scan_count = 1
    line_select_all = []
    
    # continue scan until either lines can no longer be found 
    # or none of the lines found are selected
    while line_found == True and line_selected == True:
        
        line_possible_all = []
        scan_angle = scan['scan_angle_start']
        color_mask = cv2.inRange(image_eval, scan_color, scan_color)
    
        while scan_angle < scan['scan_angle_end']:
            
            line_possible = imgstrln.stroke_lines_from_image(color_mask,
                                                             scan_color,
                                                             scan_angle,
                                                             profile_width, 
                                                             profile_length,
                                                             scan['color_match_threshold'],
                                                             scan['scan_line_offset_overlap'],
                                                             scan['scan_line_increment_overlap'])
                
            line_possible_all.extend(line_possible)
            print('scan angle complete: ', scan_angle, ' deg')                   
            print('lines found: ', len(line_possible))
            
            scan_angle += scan['scan_angle_increment']
        
#        line_segments = LineCollection(line_possible_all, linewidths = 2)
#        fig, ax = plt.subplots()
#        ax.add_collection(line_segments)
#        #ax.autoscale()
#        ax.set_xlim(0, STD_IMAGE_WIDTH)
#        ax.set_ylim(0, STD_IMAGE_HEIGHT)
#        ax.set_title('line_possible_all')
#        ax.margins(0.1)
#        plt.gca().set_aspect('equal', adjustable='box')
#        plt.show()
    
        if len(line_possible_all) == 0:
            line_found = False
        else:
            
            line_select = selctln.select_lines(line_possible_all,
                                               profile_width,
                                               profile_length,
                                               scan['select_line_width_overlap'],
                                               scan['select_line_length_overlap'],
                                               select_line_min_length)
            
            if len(line_select) == 0:
                line_selected = False
            else:
                # it isn't necessary to sort the lines and corners here,
                # just need to generate corners, and already had the sorted
                # lines and corners function created
                line_remove, \
                corner_remove = geom.sorted_lines_and_corners(line_select, 
                                                              profile_width, 
                                                              profile_length)
                
                image_eval = imgproc.color_polygon(image_eval, 
                                                   corner_remove, 
                                                   null_color)
                
                line_select_all.extend(line_select)
        
            print('lines selected: ', len(line_select))
            
        cv2.imwrite(os.path.join(DATA_PATH, 'image_eval_' + str(scan_count) + '.png'), image_eval)
            
        print("scan ", scan_count, " complete!")
        scan_count += 1
    
    if len(line_select_all) != 0:
        
#        line_segments = LineCollection(line_select_all, linewidths = 2)
#        fig, ax = plt.subplots()
#        ax.add_collection(line_segments)
#        #ax.autoscale()
#        ax.set_xlim(0, STD_IMAGE_WIDTH)
#        ax.set_ylim(0, STD_IMAGE_HEIGHT)
#        ax.set_title('line_select_all')
#        ax.margins(0.1)
#        plt.gca().set_aspect('equal', adjustable='box')
#        plt.show()
            
        cv2.imwrite(os.path.join(DATA_PATH, 'image_eval_final.png'), image_eval)
        
        line_sequence = sqnlns.sequence_lines(line_select_all, 
                                              image_prop['x_width']*image_prop['pixel_per_mm'], 
                                              image_prop['y_height']*image_prop['pixel_per_mm'], 
                                              image_prop['grid_side_pixel_length'])
        
        # If lines are less than the stroke line max length, split them into 
        # lines no longer than the stroke line max length.
        # This operation is performed at the end of the line scan operation 
        # for efficiency and effect. The result if performed before or after
        # the sequence line operation is expected to be equivalent, so the
        # operation is performed after the sequence line operation to reduce
        # the number of lines that the sequence line operation has to consider;
        # which reduces computation time. The line max length operation is 
        # performed after the longest line algorithm rather than as a
        # component of it to maintain the longest line dominance visual effect.
        line_modified = lnmaxlen.set_line_max_length(line_sequence,
                                                      stroke_line_max_length)
        
        # convert stroke line coordinates from pixels to mm
        line_final = line_modified/image_prop['pixel_per_mm']
        
        # convert to list
        line_final = line_final.tolist()
        
        print('line scan process complete!!')
        
        return line_final
        
if __name__ == '__main__':
    
    scan = scan_1
    
    start_time = time.time()
    
    with open(os.path.join(DATA_PATH, 'machine_objects.txt'), 'r') as f:
        machine_objects = json.load(f)
    f.close()
    
    machine_object_name_list = [x['name'] for x in machine_objects]
    image_prop_index = machine_object_name_list.index('image_properties')
    image_prop = machine_objects[image_prop_index]
    
    with open(os.path.join(DATA_PATH, 'image_color_center_bgr.txt'), 'r') as f:
        image_color_center = json.load(f)
    f.close()
    
    null_color = imgproc.random_non_matching_color(image_color_center)
    
    process_line = line_scan(scan, image_prop, null_color)
    
    with open(os.path.join(DATA_PATH, 'process_temp.txt'), 'w') as f:
        json.dump(scan, f, separators = (',', ':'), sort_keys = True, indent = 4)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'process_line_temp.txt'), 'w') as f:
        json.dump(process_line, f, separators = (',', ':'), sort_keys = True, indent = 4)
    f.close()
    
    print("--- %.1f seconds ---" % (time.time() - start_time))
