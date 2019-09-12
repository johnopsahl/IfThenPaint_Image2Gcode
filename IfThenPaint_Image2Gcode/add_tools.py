import os
import json
from definitions import DATA_PATH

# define all tools available to the machine

# tool length is the distance from the tool chuck to the end of the tool,
# it is not used to generate gcode, it is just used for records

tool_1 = {'name': '3_round',
          'tool_length': 10,
          'x_dock': 48,
          'y_dock': 330,
          'z_B0C0_clearance': -55,
          'z_water_dip': -132, 
          'z_towel_wipe': -74}

tool_2 = {'name': '7x2.5_flat',
          'tool_length' : 10,
          'x_dock': 113,
          'y_dock': 330,
          'z_B0C0_clearance': 0,
          'z_water_dip': -5,
          'z_towel_wipe': -5}

tool_3 = {'name': 'none_1',
          'tool_length' : 10,
          'x_dock': 178,
          'y_dock': 330,
          'z_B0C0_clearance': 0,
          'z_water_dip': -5,
          'z_towel_wipe': -5}

tool_4 = {'name': 'none_2',
          'tool_length' : 10,
          'x_dock': 243,
          'y_dock': 330,
          'z_B0C0_clearance': 0,
          'z_water_dip': -5,
          'z_towel_wipe': -5}

tools = [tool_1,
         tool_2,
         tool_3,
         tool_4]

with open(os.path.join(DATA_PATH, 'tools.txt'), 'w') as f:
    json.dump(tools, f, separators = (',', ':'), sort_keys = True, indent = 4)
f.close()