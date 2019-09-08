import os
import json
import numpy as np
import geometry as geom
from definitions import DATA_PATH

def add_layer(layer_name, process_name, tool_profile_name, paint_name=None):
    # layers top level building blocks for constructing the painting, 
    # they assign a paint color and tool profile to a paint stroke 
    # generation process, layers can be intrepreted literally as a layer of paint
    
    layer_file_path = os.path.join(DATA_PATH, 'layers.txt')
    if os.path.isfile(layer_file_path):
        with open(layer_file_path, 'r') as f:
            layers = json.load(f)
        f.close()
    else:
        layers = []
    
    if paint_name == None:
        # auto select paint that is closest to image color
        paint_name = auto_select_paint(process_name)
    
    layer = {'name': layer_name,
             'process_name': process_name, 
             'paint_name': paint_name,
             'tool_profile_name': tool_profile_name}
    
    layers.append(layer)
    
    with open(os.path.join(DATA_PATH, 'layers.txt'), 'w') as f:
        json.dump(layers, f, separators = (',', ':'), sort_keys = True, indent = 4)
    f.close()
    
def auto_select_paint(process_name):
    
    with open(os.path.join(DATA_PATH, 'processes.txt'), 'r') as f:
        processes = json.load(f)
    f.close()
    
    process_name_list = [x['name'] for x in processes]
    process_index = process_name_list.index(process_name)
    
    process_scan_color_bgr = processes[process_index]['scan_color_bgr']
    
    with open(os.path.join(DATA_PATH, 'paints.txt'), 'r') as f:
        paints = json.load(f)
    f.close()
    
    paint_color_rgb = [[x['name'], x['paint_color_rgb']] for x in paints]
    
    paint_name = match_paint_color_to_image_color(process_scan_color_bgr,
                                                  paint_color_rgb)
    
    return paint_name

def match_paint_color_to_image_color(image_color_bgr, paint_color_rgb):
    # match the closest available paint color rgb to the image color bgr
    
    r_paint = np.array([rgb[1][0] for rgb in paint_color_rgb])
    g_paint = np.array([rgb[1][1] for rgb in paint_color_rgb])
    b_paint = np.array([rgb[1][2] for rgb in paint_color_rgb])
            
    color_distance = geom.distance_3d(image_color_bgr[2],
                                      image_color_bgr[1],
                                      image_color_bgr[0],
                                      r_paint,
                                      g_paint,
                                      b_paint)
    
    # name of the paint color that is closest to the image color
    paint_name = paint_color_rgb[np.argmin(color_distance)][0]
    
    return paint_name

if __name__ == '__main__':

    #layer name, process name, tool profile name
    add_layer('black_layer', 'line_scan_black', '3_round_B0C0')
    