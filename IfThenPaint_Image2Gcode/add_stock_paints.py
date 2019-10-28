import os
import json
from definitions import DATA_PATH

# define all paints available to the machine
paint_1 = {'name': 'gray_0',
           'color_rgb': [200, 200, 200],
           'position': 0}

paint_2 = {'name': 'gray_1',
           'color_rgb': [164, 164, 164],
           'position': 1}

paint_3 = {'name': 'gray_2',
           'color_rgb': [106, 106, 106],
           'position': 2}

paint_4 = {'name': 'gray_3',
           'color_rgb': [60, 60, 60],
           'position': 3}

paint_5 = {'name': 'gray_4',
           'color_rgb': [34, 34, 34],
           'position': 4}

#paint_1 = {'name': 'red',
#           'paint_color_rgb': [255, 0, 0],
#           'dispenser_position': 0}
#
#paint_2 = {'name': 'yellow',
#           'paint_color_rgb': [255, 255, 0],
#           'dispenser_position': 1}
#
#paint_3 = {'name': 'green',
#           'paint_color_rgb': [0, 255, 0],
#           'dispenser_position': 2}
#
#paint_4 = {'name': 'blue',
#           'paint_color_rgb': [0, 0, 255],
#           'dispenser_position': 3}
#
#paint_5 = {'name': 'black',
#           'paint_color_rgb': [0, 0, 0],
#           'dispenser_position': 4}
#
#paint_6 = {'name': 'white',
#           'paint_color_rgb': [255, 255, 255],
#           'dispenser_position': 5}
#
#paint_7 = {'name': 'gray',
#           'paint_color_rgb': [128, 128, 128],
#           'dispenser_position': 6}

paints = [paint_1, 
          paint_2, 
          paint_3, 
          paint_4, 
          paint_5]

with open(os.path.join(DATA_PATH, 'stock_paints.txt'), 'w') as f:
    json.dump(paints, f, separators = (',', ':'), sort_keys = True, indent = 4)
f.close()