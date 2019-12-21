import os
import json
import cv2
import numpy as np
import image_processing as imgproc
import geometry as geom
from definitions import DATA_PATH

def create_painting_preview(layers,
                            image_prop,
                            processes,
                            process_lines,
                            tool_profiles):
    # creates an preview image of the painting using the layers that have been
    # defined
    
    image_quant = cv2.imread(os.path.join(DATA_PATH, 'image_quant.png'))
    image_height_std, image_width_std = image_quant.shape[:2]
    
    image_canvas = np.zeros((image_height_std, image_width_std, 3), np.uint8)
    image_canvas[:] = [255, 255, 255]
                    
    for layer in layers:
        
        process_name = layer['process_name']
        process_name_list = [x['name'] for x in processes]
        process_index = process_name_list.index(process_name)
        
        paint_color_rgb = layer['paint_color_rgb']
        
        tool_profile_name = layer['tool_profile_name']
        tool_profile_name_list = [x['name'] for x in tool_profiles]
        tool_profile_index = tool_profile_name_list.index(tool_profile_name)
        tool_profile = tool_profiles[tool_profile_index]
        pixel_profile_width = tool_profile['profile_width']*image_prop['pixel_per_mm']
        pixel_profile_length = tool_profile['profile_length']*image_prop['pixel_per_mm']
        
        line = np.asarray(process_lines[process_index])*image_prop['pixel_per_mm']
        
        image_canvas = add_lines_to_canvas(image_canvas,
                                           line, 
                                           paint_color_rgb,
                                           pixel_profile_width,
                                           pixel_profile_length)
        
    cv2.imwrite(os.path.join(DATA_PATH, 'painting_preview' + '.png'), 
                image_canvas)

def add_lines_to_canvas(image_canvas, 
                        line, 
                        color_rgb, 
                        pixel_profile_width, 
                        pixel_profile_length):
    # overlays lines of the proper color and width on the image
    
    line_draw, \
    corner_draw = geom.sorted_lines_and_corners(line, 
                                                pixel_profile_width, 
                                                pixel_profile_length)
    
    image_canvas = imgproc.color_polygon(image_canvas, 
                                         corner_draw, 
                                         color_rgb[::-1])
    
    return image_canvas
   
if __name__ == '__main__':
    
    with open(os.path.join(DATA_PATH, 'layers.txt'), 'r') as f:
        layers = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'image_properties.txt'), 'r') as f:
        image_prop = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'processes.txt'), 'r') as f:
        processes = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'process_lines.txt'), 'r') as f:
        process_lines = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'tool_profiles.txt'), 'r') as f:
        tool_profiles = json.load(f)
    f.close()
    
    create_painting_preview(layers,
                            image_prop,
                            processes,
                            process_lines,
                            tool_profiles)