import os
import json
from definitions import DATA_PATH

# define all tool profiles here, tool profiles are used to characterize 
# tool movement techniques and properties that are a consequence of the techniques,
# changing these parameters will influence the "physical style" of the painting

tool_profile_1 = {'name': '4_round_B0C0',
                  'tool_name': '4_round',
                  'profile_width': 3, # tool profile along x axis when A0
                  'profile_length': 3, # tool profile along y axis when A0
                  'a_axial_symmetry': 2,  # 0 -> no axial symmetry, 1 -> 180 deg axial symmetry, 2 -> infinite axial symmetry
                  'z_canvas_unload_percent': 0.3,
                  'unload_feed_rate': 2500,
                  'paint_dist_max': 200,
                  'clean_dist_max': 200*15, # must be a multiple of paint_dist_max or update map_palette to account for extra paint dip
                  'paint_dip_volume': 0.05,
                  'z_palette_load_percent': 0.4, # percent of tip_length to extend beyond palette paint bead
                  'load_feed_rate': 1500} # feed rate of tool loading operation}

tool_profile_2 = {'name': '2_round_B0C0',
                  'tool_name': '2_round',
                  'profile_width': 2.25,
                  'profile_length': 2.25,
                  'a_axial_symmetry': 2,
                  'z_canvas_unload_percent': 0.50,
                  'unload_feed_rate': 2500,
                  'paint_dist_max': 100,
                  'clean_dist_max': 100*8,
                  'paint_dip_volume': 0.05,
                  'z_palette_load_percent': 0.6,
                  'load_feed_rate': 1500}

tool_profile_3 = {'name': '2_flat_B0C0',
                  'tool_name': '2_flat',
                  'profile_width': 2.25,
                  'profile_length': 2.25,
                  'a_axial_symmetry': 1,
                  'z_canvas_unload_percent': 0.35,
                  'unload_feed_rate': 2500,
                  'paint_dist_max': 100,
                  'clean_dist_max': 100*8,
                  'paint_dip_volume': 0.05,
                  'z_palette_load_percent': 0.6,
                  'load_feed_rate': 1500}

tool_profiles = [tool_profile_1,
                 tool_profile_2,
                 tool_profile_3]

with open(os.path.join(DATA_PATH, 'tool_profiles.txt'), 'w') as f:
    json.dump(tool_profiles, f, separators = (',', ':'), sort_keys = True, indent = 4)
f.close()


    

    