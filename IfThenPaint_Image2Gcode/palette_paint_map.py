import os
import json
import math
from definitions import DATA_PATH

def palette_paint_map(layer_paint_distance, 
                      machine_objects, 
                      tool_profiles):
    # generate a map of where to dispense and what paint to dispense
    # on the palette
    
    machine_object_name_list = [x['name'] for x in machine_objects]
    paint_palette_index = machine_object_name_list.index('paint_palette')
    paint_dispenser_index = machine_object_name_list.index('paint_dispenser')
    palette = machine_objects[paint_palette_index]
    dispenser = machine_objects[paint_dispenser_index]
    
    palette_paint_map = []
    dispense_paint_volume = []
    x_current = palette['x_max'] - dispenser['x_bead_offset']
    
    for layer in layer_paint_distance:
        
        paint_color_rgb = layer['paint_color_rgb']
        
        tool_profile_name = layer['tool_profile_name']
        tool_profile_name_list = [x['name'] for x in tool_profiles]
        tool_profile_index = tool_profile_name_list.index(tool_profile_name)
        tool_profile = tool_profiles[tool_profile_index]
        paint_dist_max = tool_profile['paint_dist_max']
        brush_paint_bead_length = tool_profile['paint_bead_length']
        
        palette_y_start = palette['y_max'] - palette['y_margin']
        palette_y_end = palette['y_min'] + palette['y_margin']
        palette_length = palette_y_start - palette_y_end
        
        # calculate length of paint bead needed based on total length of 
        # strokes on canvas and required length of paint bead for each paint dip
        paint_bead_distance = math.ceil((layer['paint_distance']/paint_dist_max))*brush_paint_bead_length
        
         # limit max paint bead length to be a multiple of the brush paint bead length
        paint_bead_length_max = math.floor(palette_length/brush_paint_bead_length)*brush_paint_bead_length
        
        # calculate paint volume to determine the minimum amount of paint to
        # load into each dispenser prior to the painting
        paint_bead_volume = paint_bead_distance/10*(dispenser['paint_bead_width']/10)*(dispenser['paint_bead_height']/10)
        dispense_paint_volume.append({'paint_color_rgb': paint_color_rgb, 
                                      'paint_volume': paint_bead_volume})
        
        while paint_bead_distance > 0:
            if x_current + 1.5*dispenser['x_bead_offset'] > palette['x_min']:
                if paint_bead_distance >= paint_bead_length_max:
                    palette_paint_map.append({'paint_color_rgb': paint_color_rgb,
                                              'tool_profile_name': tool_profile_name,
                                              'x_position': x_current,
                                              'y_start': palette_y_start,
                                              'y_end': palette_y_start - paint_bead_length_max})
                    x_current -= dispenser['x_bead_offset']
                    paint_bead_distance -= paint_bead_length_max
                else:
                    palette_paint_map.append({'paint_color_rgb': paint_color_rgb,
                                              'tool_profile_name': tool_profile_name,
                                              'x_position': x_current,
                                              'y_start': palette_y_start,
                                              'y_end': palette_y_start - paint_bead_distance})
                    x_current -= dispenser['x_bead_offset']
                    paint_bead_distance = 0
            else:
                print('Too much paint, not enough palette, palette x dimension exceeded!!')
                break

    return palette_paint_map, dispense_paint_volume

if __name__ == '__main__':
        
    with open(os.path.join(DATA_PATH, 'machine_objects.txt'), 'r') as f:
        machine_objects = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'layer_paint_distance.txt'), 'r') as f:
        layer_paint_distance = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'tool_profiles.txt'), 'r') as f:
        tool_profiles = json.load(f)
    f.close()
    
    palette_paint_map, dispense_paint_volume = palette_paint_map(layer_paint_distance,
                                                                 machine_objects,
                                                                 tool_profiles)
    
    with open(os.path.join(DATA_PATH, 'dispense_paint_volume.txt'), 'w') as f:
        json.dump(dispense_paint_volume, f, separators = (',', ':'), sort_keys = True, indent = 4)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'palette_paint_map.txt'), 'w') as f:
        json.dump(palette_paint_map, f, separators = (',', ':'), sort_keys = True, indent = 4)
    f.close()