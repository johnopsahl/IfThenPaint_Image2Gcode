import os
import json
from definitions import DATA_PATH

# all machine object parameters needed to develop the gcode machine instructions,
# parameter values are specific to the If Then Paint proof-of-concept prototype machine

image_properties = {'name': 'image_properties',
                    'x_width': 120,
                    'y_height': 160,
                    'pixel_per_mm': 6.4,
                    'grid_side_pixel_length': 64}

canvas = {'name': 'canvas',
          'x_min': 136,
          'y_min': 103,
          'x_width': 127,
          'y_height': 177.8}

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
                    'b_max_travel': 90,
                    'x_workspace': 7} #x distance to position palette within workspace

paint_palette = {'name': 'paint_palette',
                 'x_min': 279,
                 'x_max': 379,
                 'x_margin': 10,
                 'y_min': 133,
                 'y_max': 333,
                 'y_margin': 10,
                 'z_top': 21} 

paint_water = {'name': 'paint_water',
               'y_water': 36,
               'z_water': 3,
               'z_clearance': 32}

paint_dispenser = {'name': 'paint_dispenser',
                   'angle_btw_dispensers': 36,
                   'z_clearance': 8, # relative to top of paint palette
                   'b_clearance': 22, # so b-axis push plate clears syringe plungers
                   'syringe_volume': 8, #syringe volume capacity
                   'dispense_mm_per_ml': 5.8, # mm of syringe movement to dispense one ml
                   'dispense_delay': 2,
                   'dispense_feedrate': 50,
                   'b_probe_retract': 2,
                   'b_probe_feedrate': 1200}

machine_objects = [image_properties,
                   canvas,
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
