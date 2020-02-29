import os
import json
from definitions import DATA_PATH

# define all paints available to the machine
paint_color_1 = {'color_rgb': [255, 0, 0],
                 'paint_color_comp': [[[255, 0, 0], 1]]}

paint_color_2 = {'color_rgb': [255, 255, 0],
                 'paint_color_comp': [[[255, 255, 0], 1]]}

paint_color_3 = {'color_rgb': [0, 255, 0],
                 'paint_color_comp': [[[0, 255, 0], 1]]}

paint_color_4 = {'color_rgb': [0, 0, 255],
                 'paint_color_comp': [[[0, 0, 255], 1]]}

paint_color_5 = {'color_rgb': [0, 0, 0],
                 'paint_color_comp': [[[0, 0, 0], 1]]}

paint_color_6 = {'color_rgb': [255, 255, 255],
                 'paint_color_comp': [[[255, 255, 255], 1]]}

paint_color_7 = {'color_rgb': [200, 200, 200],
                 'paint_color_comp': [[[0, 0, 0], 0.22],
                                      [[255, 255, 255], 0.78]]}

paint_color_8 = {'color_rgb': [164, 164, 164],
                 'paint_color_comp': [[[0, 0, 0], 0.36],
                                      [[255, 255, 255], 0.64]]}

paint_color_9 = {'color_rgb': [106, 106, 106],
                 'paint_color_comp': [[[0, 0, 0], 0.59],
                                      [[255, 255, 255], 0.41]]}

paint_color_10 = {'color_rgb': [60, 60, 60],
                 'paint_color_comp': [[[0, 0, 0], 0.77],
                                      [[255, 255, 255], 0.23]]}
                 
paint_color_11 = {'color_rgb': [0, 130, 0],
                 'paint_color_comp': [[[0, 255, 0], 0.7],
                                      [[0, 0, 0], 0.3]]}

paint_color_12 = {'color_rgb': [108, 108, 255],
                 'paint_color_comp': [[[0, 0, 255], 0.6],
                                      [[255, 255, 255], 0.4]]}

paint_colors = [paint_color_1, 
                paint_color_2, 
                paint_color_3, 
                paint_color_4, 
                paint_color_5,
                paint_color_6,
                paint_color_7,
                paint_color_8,
                paint_color_9,
                paint_color_10,
                paint_color_11,
                paint_color_12]

with open(os.path.join(DATA_PATH, 'paint_colors.txt'), 'w') as f:
    json.dump(paint_colors, f, separators = (',', ':'), sort_keys = True, indent = 4)
f.close()