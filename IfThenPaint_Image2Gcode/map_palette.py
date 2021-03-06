import os
import json
import numpy as np
from definitions import DATA_PATH

def map_palette(layer_paint_dips,
                paint_colors,
                machine_objects, 
                tool_profiles,
                tools):
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
    
    palette_brush_map = []
    palette_paint_map = []
    x_current = palette_x_start
    
    for layer in layer_paint_dips:
        
        paint_color_rgb = layer['paint_color_rgb']
        paint_color_rgb_list = [x['color_rgb'] for x in paint_colors]
        paint_color_rgb_index = paint_color_rgb_list.index(paint_color_rgb)
        paint_color = paint_colors[paint_color_rgb_index]

        tool_profile_name = layer['tool_profile_name']
        tool_profile_name_list = [x['name'] for x in tool_profiles]
        tool_profile_index = tool_profile_name_list.index(tool_profile_name)
        tool_profile = tool_profiles[tool_profile_index]
        
        tool_name_list = [x['name'] for x in tools]
        tool_name = tool_profile['tool_name']
        tool_index = tool_name_list.index(tool_name)
        tool = tools[tool_index]
        
        paint_dip_volume = tool_profile['paint_dip_volume']
        
        # calculate gap between paint rows
        max_profile_dim = max(tool['profile_width'], tool['profile_length'])
        x_increment = 1.5*max_profile_dim
        
        # determine largest volume percentage of any one stock paint 
        # of the paint color composition
        paint_percent_list = [x[1] for x in paint_color['paint_color_comp']]
        max_paint_percent = max(paint_percent_list)
        
        # calculate max bead height and max bead width
        max_bead_height, max_bead_diameter = paint_bead_dimensions(max_paint_percent*paint_dip_volume)
        
        # calculate bead group length for the layer
        bead_group_length =  0
        for paint_percent in paint_percent_list:
            bead_height, bead_diameter = paint_bead_dimensions(paint_percent*paint_dip_volume)
            bead_group_length += bead_diameter
        
        # increment between columns of each paint row
        y_increment = bead_group_length + max_profile_dim
        
        # calculate number of paint beads per y row
        max_beads_per_row = np.floor(palette_y_dist/y_increment)
        
        #paints to be dispensed in order of increasing volume
        paint_percent_index = np.argsort(np.array(paint_percent_list))
        
        bead_count = layer['paint_dips']
        
        # interate until all paint beads have been dispensed
        while bead_count > 0:
            
            # if not enough x palette space to fit all paints, stop the process
            # and wrtie message to the console, occurs after x_current is already 
            # less than palette_x_end and invalid dispense row has been 
            # written to the paint_palette_map
            if x_current > palette_x_end:
                
                if bead_count >= max_beads_per_row:
                    beads_per_row = max_beads_per_row
                else:
                    # add one to account for first bead of each row as scrap
                    beads_per_row = bead_count + 1
                
                y_start = palette_y_start - y_increment/2
                y_end = y_start - beads_per_row*y_increment
                
                palette_brush_map.append({'paint_color_rgb': paint_color_rgb,
                                          'tool_profile_name': tool_profile_name,
                                          'bead_group_length': bead_group_length,
                                          'max_bead_height': max_bead_height,
                                          'max_bead_diameter': max_bead_diameter,
                                          'y_increment': y_increment,
                                          'x_row': x_current - x_increment - bead_group_length/2,
                                          'y_start': y_start - y_increment, # advance by y_increment for first bead scrap
                                          'y_end': y_end})
                
                # first increment between paint color rows
                x_current -= x_increment
                
                # for each stock paint that is mixed together to create the paint color
                for i in range(len(paint_color['paint_color_comp'])):
                    
                    stock_paint = paint_color['paint_color_comp'][paint_percent_index[i]]
                    stock_paint_color = stock_paint[0]
                    stock_paint_percent = stock_paint[1]
                    
                    # capture paint volume here so as to include scrap dispense
                    # at start of each row
                    paint_volume = beads_per_row*stock_paint_percent*paint_dip_volume
                    plunger_dist = stock_paint_percent*paint_dip_volume*dispenser['dispense_mm_per_ml']
                    
                    bead_height, bead_diameter = paint_bead_dimensions(stock_paint_percent*paint_dip_volume)
                    
                    # increment to paint bead center
                    x_current -= bead_diameter/2
    
                    palette_paint_map.append({'paint_color_rgb': stock_paint_color,
                                              'tool_profile_name': tool_profile_name,
                                              'paint_bead_volume': stock_paint_percent*paint_dip_volume,
                                              'paint_volume': paint_volume,
                                              'plunger_dist': plunger_dist,
                                              'bead_height': bead_height,
                                              'y_increment': y_increment,
                                              'x_row': x_current,
                                              'y_start': y_start,
                                              'y_end': y_end})
                    
                    # increment to end of paint bead
                    x_current -= bead_diameter/2
                
                # first increment between paint color rows
                x_current -= x_increment
                
                # subtract one to account for first bead of each row as scrap
                bead_count -= beads_per_row - 1
            
            else:
                print('Too much paint, not enough palette, palette x dimension exceeded!!')
                break

    return palette_brush_map, palette_paint_map

def paint_bead_dimensions(paint_volume):
    # paint volume in ml
    
    bead_height = 33.333*paint_volume + 0.833
    bead_diameter = 40*paint_volume + 4.8
        
    return bead_height, bead_diameter
    
if __name__ == '__main__':
    
    with open(os.path.join(DATA_PATH, 'paint_colors.txt'), 'r') as f:
        paint_colors = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'layer_paint_dips.txt'), 'r') as f:
        layer_paint_dips = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'machine_objects.txt'), 'r') as f:
        machine_objects = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'tool_profiles.txt'), 'r') as f:
        tool_profiles = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'tools.txt'), 'r') as f:
        tools = json.load(f)
    f.close()
    
    palette_brush_map, palette_paint_map = map_palette(layer_paint_dips,
                                                       paint_colors,
                                                       machine_objects,
                                                       tool_profiles,
                                                       tools)
    
#    with open(os.path.join(DATA_PATH, 'dispense_paint_volume.txt'), 'w') as f:
#        json.dump(dispense_paint_volume, f, separators = (',', ':'), sort_keys = True, indent = 4)
#    f.close()
    
    with open(os.path.join(DATA_PATH, 'palette_brush_map.txt'), 'w') as f:
        json.dump(palette_brush_map, f, separators = (',', ':'), sort_keys = True, indent = 4)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'palette_paint_map.txt'), 'w') as f:
        json.dump(palette_paint_map, f, separators = (',', ':'), sort_keys = True, indent = 4)
    f.close()