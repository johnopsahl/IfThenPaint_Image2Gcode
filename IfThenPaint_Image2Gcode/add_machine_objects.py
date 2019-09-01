import os
import json
from definitions import DATA_PATH

# all machine object parameters needed to develop the gcode machine instructions,
# parameter values are specific to the If Then Paint proof-of-concept prototype machine

canvas = {'name': 'canvas',
          'x_left': 136,
          'y_bottom': 103,
          'x_length': 120,
          'y_length': 160}

brush_palette = {'name': 'brush_palette',
                 'x_min': 8,
                 'x_max': 108,
                 'y_min': 90,
                 'y_max': 290}
    
brush_water = {'name': 'brush_water',
               'x_center': 244,
               'y_center': 39,
               'dip_radius': 15,
               'feed_rate': 2500}

towel = {'name': 'towel',
         'x_current': 185, # initialize as x start
         'x_increment': 7.5,
         'x_end': 35,
         'y_center': 30,
         'wipe_radius': 15,
         'feed_rate': 2500}

tool_change = {'name': 'tool_change',
               'z_clearance': 15, # relative to end of tool
               'z_dock': -366,
               'a_start': 90,
               'c_start': 0,
               'z_screw': 2.5,
               'c_screw': 1190.59}

paint_management = {'name': 'paint_management',
                    'y_home_start_offset': 250, # go to position prior to homing
                    'x_workspace': -6} #x distance to position palette within workspace

paint_palette = {'name': 'paint_palette',
                 'x_min': 363,
                 'x_max': 263,
                 'y_min': 123,
                 'y_max': 323,
                 'z_top': -7} 

paint_water = {'name': 'paint_water',
               'y_water': 21,
               'z_water': -15.5,
               'z_clearance': -5}

paint_dispenser = {'name': 'paint_dispenser',
                   'angle_btw_dispensers': 36,
                   'paint_bead_width': 4,
                   'paint_bead_height': 2,
                   'x_bead_offset': 10,
                   'z_clearance': 8, # relative to top of paint palette
                   'b_clearance': 4, # relative to top of paint palette
                   'b_initial_dispense': 0.75,
                   'b_axis_max': 52,
                   'b_dispense_rate': 10/6}

machine_objects = [canvas,
                   brush_palette,
                   brush_water,
                   towel,
                   paint_palette,
                   tool_change,
                   paint_water,
                   paint_dispenser]

with open(os.path.join(DATA_PATH, 'machine_objects.txt'), 'w') as f:
    json.dump(machine_objects, f, separators = (',', ':'), sort_keys = True, indent = 4)
f.close()
