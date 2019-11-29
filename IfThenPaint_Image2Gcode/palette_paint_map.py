import os
import json
import numpy as np
from definitions import DATA_PATH

def palette_paint_map(layer_paint_distance,
                      paint_colors,
                      machine_objects, 
                      tool_profiles):
    # generate a map of where to dispense and what paint to dispense
    # on the palette
    
    machine_object_name_list = [x['name'] for x in machine_objects]
    paint_palette_index = machine_object_name_list.index('paint_palette')
    paint_dispenser_index = machine_object_name_list.index('paint_dispenser')
    palette = machine_objects[paint_palette_index]
    dispenser = machine_objects[paint_dispenser_index]
    
    # dispense paint on pallette from positive to negative y
    palette_y_start = palette['y_max'] - palette['y_margin']
    palette_y_end = palette['y_min'] + palette['y_margin']
    palette_y_dist = abs(palette_y_end - palette_y_start)
    
    # dispense paint on palette from positive to negative x
    palette_x_start = palette['x_max'] - palette['x_margin']
    palette_x_end = palette['x_min'] + palette['x_margin']
    palette_x_dist = abs(palette_x_end - palette_x_start)
        
    palette_paint_map = []
#    dispense_paint_volume = []
    x_current = palette_x_start
    
    for layer in layer_paint_distance:
        
        paint_color_rgb = layer['paint_color_rgb']
        paint_color_rgb_list = [x['color_rgb'] for x in paint_colors]
        paint_color_rgb_index = paint_color_rgb_list.index(paint_color_rgb)
        paint_color = paint_colors[paint_color_rgb_index]

        tool_profile_name = layer['tool_profile_name']
        tool_profile_name_list = [x['name'] for x in tool_profiles]
        tool_profile_index = tool_profile_name_list.index(tool_profile_name)
        tool_profile = tool_profiles[tool_profile_index]
        paint_dispense_volume = tool_profile['paint_dispense_volume']
        profile_width = tool_profile['profile_width']
        profile_length = tool_profile['profile_length']
        
        # determine largest volume percentage of any one stock paint 
        # of the paint color composition
        paint_percent_list = [x[1] for x in paint_color['paint_color_comp']]
        max_paint_percent = paint_percent_list.index(max(paint_percent_list))
        
        # calculate max bead height and max bead width
        max_bead_height, max_bead_width = paint_bead_dimensions(max_paint_percent*paint_dispense_volume)
        
        # use widest of the paint width, profile width, and profile length
        bead_y_increment = max(max_bead_width, profile_width, profile_length)
        
        # calculate width of paint bead stack up for each layer
        bead_x_increment =  0
        for paint_percent in paint_percent_list:
            bead_height, bead_width = paint_bead_dimensions(paint_percent*paint_dispense_volume)
            bead_x_increment += bead_width
        
        # calculate number of paint beads per y row
        max_beads_per_row = np.floor(palette_y_dist/bead_y_increment)
        
        # the first bead of each row is for ensuring proper paint flow;
        # and will not be used to load the brush
        max_beads_per_row -= 1
        
        # calculate number of paint rows and remainder of last row
        number_of_rows = np.ceil(layer['paint_dips']/max_beads_per_row)
        beads_per_last_row = layer['paint_dips'] % max_beads_per_row
        
        # detemine paints to be dispensed in order of decreasing volume
        paint_percent_index = np.argsort(np.array(paint_percent_list))
        
        # for each paint bead row
        for i in range(0, number_of_rows):
            
            if i == number_of_rows - 1:
                beads_per_row = beads_per_last_row
            else:
                beads_per_row = max_beads_per_row
            
            if beads_per_row != 0:
                
                # for each stock paint that is mixed together to create the paint color
                for j in range(0, len(paint_color['paint_color_comp'])):
                    
                    stock_paint = paint_color['paint_color_comp'][paint_percent_index[j]]
                    stock_paint_color = stock_paint[0]
                    stock_paint_percent = stock_paint[1]
                    
                    plunger_dist = stock_paint_percent*paint_dispense_volume*dispenser['dispense_mm_per_ml']
                    
                    bead_height, bead_width = paint_bead_dimensions(stock_paint_percent*paint_dispense_volume)
                    
                    x_current -= bead_width/2
                    y_start = palette_y_start - bead_width/2
                    y_end = y_start - beads_per_row*bead_y_increment
                    
                    palette_paint_map.append({'paint_color_rgb': stock_paint_color,
                                              'tool_profile_name': tool_profile_name,
                                              'plunger_dist': plunger_dist,
                                              'bead_height': bead_height,
                                              'bead_y_increment': bead_y_increment,
                                              'x_row': x_current,
                                              'y_start': y_start,
                                              'y_end': y_end})
                    
                    x_current -= bead_width/2
            
            x_current -= bead_y_increment
        
        # calculate paint volume to determine the minimum amount of paint to
        # load into each dispenser prior to the painting
        
        # temporarily comment out until, bead width prediction has been 
        # experimentally validated
#        paint_bead_volume = paint_bead_distance/10*(dispenser['paint_bead_width']/10)*(dispenser['paint_bead_height']/10)
#        dispense_paint_volume.append({'paint_color_rgb': paint_color_rgb, 
#                                      'paint_volume': paint_bead_volume})

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

    return palette_paint_map

def paint_bead_dimensions(paint_volume):
    
    # convert ml to mm^3
    paint_volume = paint_volume*1000
    
    bead_height = ((0.5*paint_volume)/(math.pi))**(1/3) # experimentally determined, based on volume of sphere
    bead_width = 2*dispense_height # assuming half sphere bead
        
    return bead_height, bead_width
    
if __name__ == '__main__':
    
    with open(os.path.join(DATA_PATH, 'paint_colors.txt'), 'r') as f:
        paint_colors = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'layer_paint_distance.txt'), 'r') as f:
        layer_paint_distance = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'machine_objects.txt'), 'r') as f:
        machine_objects = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'tool_profiles.txt'), 'r') as f:
        tool_profiles = json.load(f)
    f.close()
    
    palette_paint_map = palette_paint_map(layer_paint_distance,
                                          paint_colors,
                                          machine_objects,
                                          tool_profiles)
    
#    with open(os.path.join(DATA_PATH, 'dispense_paint_volume.txt'), 'w') as f:
#        json.dump(dispense_paint_volume, f, separators = (',', ':'), sort_keys = True, indent = 4)
#    f.close()
    
    with open(os.path.join(DATA_PATH, 'palette_paint_map.txt'), 'w') as f:
        json.dump(palette_paint_map, f, separators = (',', ':'), sort_keys = True, indent = 4)
    f.close()