import os
import json
from definitions import DATA_PATH

# define all stock paints available to the machine

paint_1 = {'color_name': 'red',
           'color_rgb': [255, 0, 0],
           'position': 0}

paint_2 = {'color_name': 'yellow',
           'color_rgb': [255, 255, 0],
           'position': 1}

paint_3 = {'color_name': 'green',
           'color_rgb': [0, 255, 0],
           'position': 2}

paint_4 = {'color_name': 'blue',
           'color_rgb': [0, 0, 255],
           'position': 3}

paint_5 = {'color_name': 'black',
           'color_rgb': [0, 0, 0],
           'position': 4}

paint_6 = {'color_name': 'white',
           'color_rgb': [255, 255, 255],
           'position': 5}

stock_paints = [paint_1, 
                paint_2, 
                paint_3, 
                paint_4, 
                paint_5,
                paint_6]

with open(os.path.join(DATA_PATH, 'stock_paints.txt'), 'w') as f:
    json.dump(stock_paints, f, separators = (',', ':'), sort_keys = True, indent = 4)
f.close()