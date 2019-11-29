import os
import json
import numpy as np
import geometry as geom
from definitions import DATA_PATH

def layer_paint_distance(layers,
                         processes,
                         process_lines,
                         tool_profiles):
    # generates a list of how far the tool travels on the canvas for each layer
    
    paint_distance = []
    
    for layer in layers:
        
        process_name = layer['process_name']
        process_name_list = [x['name'] for x in processes]
        process_index = process_name_list.index(process_name)
        
        tool_profile_name = layer['tool_profile_name']
        tool_profile_name_list = [x['name'] for x in tool_profiles]
        tool_profile_index = tool_profile_name_list.index(tool_profile_name)
        tool_profile = tool_profiles[tool_profile_index]
        
        paint_color_rgb = layer['paint_color_rgb']

        distance_on_canvas = canvas_paint_distance(process_lines[process_index])
        paint_dips = np.ceil(distance_on_canvas/tool_profile['paint_dist_max'])
        
        paint_distance.append({'paint_color_rgb': paint_color_rgb,
                               'tool_profile_name': tool_profile_name,
                               'paint_distance': distance_on_canvas,
                               'paint_dips': paint_dips})
    
    return paint_distance

def canvas_paint_distance(line):
    # calculate distance tool travels on the canvas
    
    paint_distance = 0
    
    line = np.asarray(line)

    line_length = geom.length_of_line(line)
    
    paint_distance += np.sum(line_length)
        
    return paint_distance

if __name__ == '__main__':
    
    with open(os.path.join(DATA_PATH, 'layers.txt'), 'r') as f:
        layers = json.load(f)
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
    
    paint_distance = layer_paint_distance(layers, 
                                          processes, 
                                          process_lines,
                                          tool_profiles)
    
    with open(os.path.join(DATA_PATH, 'layer_paint_distance.txt'), 'w') as f:
        json.dump(paint_distance, f, separators = (',', ':'), sort_keys = True, indent = 4)
    f.close()