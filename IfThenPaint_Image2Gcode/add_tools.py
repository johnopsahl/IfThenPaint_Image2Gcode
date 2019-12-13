import os
import json
from definitions import DATA_PATH

# define all tools available to the machine

tool_1 = {'name': '4_round',
          'length': 10, # distance from tool chuck to end of tool; currently not used
          'tip_length': 4, # length of tool measured from tip (i.e. bristle length); currently not used
          'x_dock': 48,
          'y_dock': 330,
          'z_B0C0_clearance': -55,
          'z_water_dip': -132, 
          'z_towel_wipe': -74}

tool_2 = {'name': '2_round',
          'length' : 10,
          'tip_length': 4,
          'x_dock': 113,
          'y_dock': 330,
          'z_B0C0_clearance': -55,
          'z_water_dip': -132,
          'z_towel_wipe': -74}

tool_3 = {'name': 'none_1',
          'length' : 10,
          'tip_length': 4,
          'x_dock': 178,
          'y_dock': 330,
          'z_B0C0_clearance': 0,
          'z_water_dip': -132,
          'z_towel_wipe': -74}

tool_4 = {'name': 'none_2',
          'length' : 10,
          'tip_length': 4,
          'x_dock': 243,
          'y_dock': 330,
          'z_B0C0_clearance': 0,
          'z_water_dip': -132,
          'z_towel_wipe': -74}

tools = [tool_1,
         tool_2,
         tool_3,
         tool_4]

with open(os.path.join(DATA_PATH, 'tools.txt'), 'w') as f:
    json.dump(tools, f, separators = (',', ':'), sort_keys = True, indent = 4)
f.close()