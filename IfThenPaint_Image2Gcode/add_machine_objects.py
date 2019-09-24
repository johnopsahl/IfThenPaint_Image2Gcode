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
                 'x_min': 11,
                 'x_max': 111,
                 'y_min': 92,
                 'y_max': 292}
    
brush_water = {'name': 'brush_water',
               'x_center': 244,
               'y_center': 39,
               'dip_radius': 17,
               'feed_rate': 2500}

towel = {'name': 'towel',
         'x_current': 185, # initialize as x start
         'x_increment': 7.5,
         'x_end': 35,
         'y_center': 30,
         'wipe_radius': 15,
         'feed_rate': 2500}

tool_change = {'name': 'tool_change',
               'z_dock': -181,
               'a_start': 0,
               'c_start': 0,
               'z_screw': 3.5,
               'c_screw': 1333.5}

paint_management = {'name': 'paint_management',
                    'y_max_travel': 336,
                    'b_max_travel': 98,
                    'x_workspace': 7} #x distance to position palette within workspace

paint_palette = {'name': 'paint_palette',
                 'x_min': 279,
                 'x_max': 379,
                 'y_min': 233,
                 'y_max': 333,
                 'y_margin': 10,
                 'z_top': 19} 

paint_water = {'name': 'paint_water',
               'y_water': 36,
               'z_water': 2,
               'z_clearance': 27}

paint_dispenser = {'name': 'paint_dispenser',
                   'angle_btw_dispensers': 36,
                   'paint_bead_width': 5.75,
                   'paint_bead_height': 2,
                   'x_bead_offset': 12,
                   'z_clearance': 8, # relative to top of paint palette
                   'b_clearance': 4,
                   'b_initial_dispense': 0.3,
                   'b_dispense_rate': 0.25/10,
                   'b_probe_retract': 2,
                   'b_feedrate': 1000}

machine_objects = [canvas,
                   brush_palette,
                   brush_water,
                   towel,
                   paint_palette,
                   paint_management,
                   tool_change,
                   paint_water,
                   paint_dispenser]

with open(os.path.join(DATA_PATH, 'machine_objects.txt'), 'w') as f:
    json.dump(machine_objects, f, separators = (',', ':'), sort_keys = True, indent = 4)
f.close()
