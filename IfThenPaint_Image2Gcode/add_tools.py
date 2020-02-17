import os
import json
from definitions import DATA_PATH

# define all tools available to the machine

tool_1 = {'name': '4_round',
          'length': 62.5, # distance from tool chuck end to end of tool tip
          'tip_length': 14, # length of tool measured from tip (i.e. bristle length)
          'x_dock': 48,
          'y_dock': 328,
          'z_workspace_clearance': -60,
          'z_water_dip_percent': 0.3, # percent of tip_length to extend beyond water z_bottom
          'z_towel_wipe_percent': 0.5} # percent of tip_length to extend beyond towel z_top

tool_2 = {'name': '2_round',
          'length' : 62.5 + 3.2, # 3.2mm is chuck length add
          'tip_length': 16,
          'x_dock': 113,
          'y_dock': 328,
          'z_workspace_clearance': -60,
          'z_water_dip_percent': 0.3,
          'z_towel_wipe_percent': 0.5}

tool_3 = {'name': '2_flat',
          'length' : 57,
          'tip_length': 6.5,
          'x_dock': 178,
          'y_dock': 328,
          'z_workspace_clearance': -60,
          'z_water_dip_percent': 0.3,
          'z_towel_wipe_percent': 0.5}

tool_4 = {'name': 'none',
          'length' : 10,
          'tip_length': 4,
          'x_dock': 243,
          'y_dock': 328,
          'z_workspace_clearance': 0,
          'z_water_dip_percent': 0.85,
          'z_towel_wipe_percent': 0.85}

tools = [tool_1,
         tool_2,
         tool_3,
         tool_4]

with open(os.path.join(DATA_PATH, 'tools.txt'), 'w') as f:
    json.dump(tools, f, separators = (',', ':'), sort_keys = True, indent = 4)
f.close()