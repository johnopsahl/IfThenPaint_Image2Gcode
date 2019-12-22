import os
import json
from definitions import DATA_PATH

# all machine object parameters needed to develop the gcode machine instructions,
# parameter values are specific to the If Then Paint proof-of-concept prototype machine

canvas = {'name': 'canvas',
          'x_min': 136,
          'x_max': 263,
          'y_min': 99.5,
          'y_max': 277.3,
          'z_top': -128}

brush_palette = {'name': 'brush_palette',
                 'x_min': 9.5,
                 'x_max': 109.5,
                 'y_min': 88,
                 'y_max': 288,
                 'z_top': -138.75} # end of tool chuck at top of palette when b axis at 0
    
brush_water = {'name': 'brush_water',
               'x_center': 242,
               'y_center': 39,
               'z_bottom': -131 - 66.6 + 8.6, # end of tool chuck at brush water bottom when b axis at 0
               'dip_radius': 17,
               'feed_rate': 2500}

towel = {'name': 'towel',
         'x_current': 185, # initialize as x start
         'x_increment': 7.5,
         'x_end': 35,
         'y_center': 25,
         'z_top': -129.5, # end of tool chuck at top of towel when b axis is 0
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
                    'x_workspace': 8} #x distance to position palette within workspace

paint_palette = {'name': 'paint_palette',
                 'x_min': 276,
                 'x_max': 376,
                 'x_margin': 10,
                 'y_min': 134.5,
                 'y_max': 334.5,
                 'y_margin': 10,
                 'z_top': 22} # location at which dispener contacts palettte

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
