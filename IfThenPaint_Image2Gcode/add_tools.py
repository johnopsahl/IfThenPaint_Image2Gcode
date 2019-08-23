import os
import json
from definitions import DATA_PATH

# define all tools available to the machine
tool_1 = {'name': '7x2.5_flat',
          'x_dock': 156.5,
          'y_dock': 249.75}

tool_2 = {'name': '3_round',
          'x_dock': 160.5,
          'y_dock': 200}

tools = [tool_1,
         tool_2]

with open(os.path.join(DATA_PATH, 'tools.txt'), 'w') as f:
    json.dump(tools, f, separators = (',', ':'), sort_keys = True, indent = 4)
f.close()