import os
import json
from definitions import DATA_PATH

# all machine object parameters needed to develop the gcode machine instructions,
# parameter values are specific to the If Then Paint proof-of-concept prototype machine

canvas = {'name': 'canvas',
          'x_left': 4,
          'y_bottom': 9.75,
          'z_top': 3,
          'x_length': 120,
          'y_length': 160}

brush_palette = {'name': 'brush_palette',
                 'x_min': 0,
                 'x_max': 100,
                 'y_min': 0,
                 'y_max': 200,
                 'z_top': 2}
    
brush_water = {'name': 'brush_water',
               'x_center': 164,
               'y_center': -45.25,
               'z_dip': -62,
               'dip_radius': 15,
               'feed_rate': 2500}

towel = {'name': 'towel',
         'x_current': 12.5,
         'x_increment': 7.5,
         'x_end': 175,
         'y_center': 169,
         'z_wipe': -5,
         'wipe_radius': 15,
         'feed_rate': 2500}

tool_change = {'name': 'tool_change',
               'z_clearance': 15,
               'z_dock': -11.5,
               'a_start': 90,
               'c_start': 0,
               'z_screw': 2.5,
               'c_screw': 1190.59}

paint_palette = {'name': 'paint_palette',
                 'x_min': 0,
                 'x_max': 100,
                 'y_min': 0,
                 'y_max': 200,
                 'z_top': 2}

paint_water = {'name': 'paint_water',
               'x_center': 164,
               'y_center': -45.25,
               'z_top': -62}

paint_dispenser = {'name': 'paint_dispenser',
                   'angle_btw_dispensers': 36,
                   'paint_bead_width': 4,
                   'paint_bead_height': 2,
                   'x_bead_offset': 10,
                   'z_clearance': 10,
                   'z_dispense': 3,
                   'b_clearance': 5,
                   'b_initial_dispense': 0.75,
                   'b_axis_max': 30,
                   'b_dispense_rate': 10/6}

machine_objects = [canvas,
                   brush_palette,
                   brush_water,
                   towel,
                   paint_palette,
                   paint_water,
                   paint_dispenser]

with open(os.path.join(DATA_PATH, 'machine_objects.txt'), 'w') as f:
    json.dump(machine_objects, f, separators = (',', ':'), sort_keys = True, indent = 4)
f.close()
