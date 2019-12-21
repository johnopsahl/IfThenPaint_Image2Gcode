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

with open(os.path.join(DATA_PATH, 'image_properties.txt'), 'w') as f:
    json.dump(image_properties, f, separators = (',', ':'), sort_keys = True, indent = 4)
f.close()
