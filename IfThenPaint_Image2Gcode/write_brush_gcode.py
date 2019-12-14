import os
import json
import numpy as np
import lines_to_gcode as ln2gcd
import datetime
from definitions import DATA_PATH

def write_brush_gcode(project_name,
                      machine_objects,
                      paint_colors,
                      tools,
                      tool_profiles,
                      layers,
                      processes,
                      process_lines,
                      palette_brush_map):
    # generates the gcode file used by the six axis brush cnc machine to 
    # paint on the canvas
    
    timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    
    gcode_file = open(os.path.join(DATA_PATH, str(project_name) + '_brush' + '.gcode'), 'w')
    
    gcode_file.write('%\n') # start of gcode file
    gcode_file.write('(PROJECT, ' + str(project_name) + ')\n')
    gcode_file.write('(TIMESTAMP, ' + timestamp + ')\n')
    gcode_file.write('\n')
    
    machine_object_name_list = [x['name'] for x in machine_objects]
    image_prop_index = machine_object_name_list.index('image_properties')
    canvas_index = machine_object_name_list.index('canvas')
    brush_palette_index = machine_object_name_list.index('brush_palette')
    brush_water_index = machine_object_name_list.index('brush_water')
    towel_index = machine_object_name_list.index('towel')
    tool_change_index = machine_object_name_list.index('tool_change')
    paint_palette_index = machine_object_name_list.index('paint_palette')
    
    image_prop = machine_objects[image_prop_index]
    canvas = machine_objects[canvas_index]
    brush_palette = machine_objects[brush_palette_index]
    brush_water = machine_objects[brush_water_index]
    towel = machine_objects[towel_index]
    tool_change = machine_objects[tool_change_index]
    paint_palette = machine_objects[paint_palette_index]
    
    # convert paint palette map from paint palette coordinates
    # to brush palette coordinates
    palette_x_offset = brush_palette['x_max'] - paint_palette['x_max']
    palette_y_offset = brush_palette['y_max'] - paint_palette['y_max']
    
    for paint_row in palette_brush_map:
        paint_row['x_row'] += palette_x_offset
        paint_row['y_start'] += palette_y_offset
        paint_row['y_end'] += palette_y_offset
        
    # write object parameters to gcode file
    gcode_file.write('(IMAGE PROPERTIES)\n')
    for key in image_prop:
        gcode_file.write('(' + str(key) + ' , ' + str(image_prop[key]) + ')\n')
    gcode_file.write('\n')

    gcode_file.write('(CANVAS)\n')
    for key in canvas:
        gcode_file.write('(' + str(key) + ' , ' + str(canvas[key]) + ')\n')
    gcode_file.write('\n')
    
    gcode_file.write('(BRUSH PALETTE)\n')
    for key in brush_palette:
        gcode_file.write('(' + str(key) + ' , ' + str(brush_palette[key]) + ')\n')
    gcode_file.write('\n')
    
    gcode_file.write('(BRUSH WATER)\n')
    for key in brush_water:
        gcode_file.write('(' + str(key) + ' , ' + str(brush_water[key]) + ')\n')
    gcode_file.write('\n')
    
    gcode_file.write('(TOWEL)\n')
    for key in towel:
        gcode_file.write('(' + str(key) + ' , ' + str(towel[key]) + ')\n')
    gcode_file.write('\n')
    
    gcode_file.write('(TOOL CHANGE)\n')
    for key in tool_change:
        gcode_file.write('(' + str(key) + ' , ' + str(tool_change[key]) + ')\n')
    gcode_file.write('\n')
    
    gcode_file.write('G17 G21 G90 G94 G54\n') # initialization block
    # G17 -> G02 and G03 commands about the XY plane
    # G21 -> units of millimeters
    # G90 -> absolute coordinates
    # 694 -> feed rate in distance/minute units
    # G54 -> workspace coordinates
    go_to_home(gcode_file)
    gcode_file.write('\n')
    
    tool_current = None 
    
    for layer in layers:          
        
        process_name = layer['process_name']
        tool_profile_name = layer['tool_profile_name']
        paint_color_rgb = layer['paint_color_rgb']
        
        process_name_list = [x['name'] for x in processes]
        tool_profile_name_list = [x['name'] for x in tool_profiles]
        tool_name_list = [x['name'] for x in tools]
        paint_color_rgb_list = [x['color_rgb'] for x in paint_colors]
        
        process_index = process_name_list.index(process_name)
        tool_profile_index = tool_profile_name_list.index(tool_profile_name)
        paint_color_index = paint_color_rgb_list.index(paint_color_rgb)
        
        process = processes[process_index]
        process_line = process_lines[process_index]
        tool_profile = tool_profiles[tool_profile_index]
        paint_color = paint_colors[paint_color_index]
        
        tool_name = tool_profile['tool_name']
        tool_index = tool_name_list.index(tool_name)
        tool = tools[tool_index]
        
        # write object parameters to gcode file
        gcode_file.write('(************************************************)\n')
        gcode_file.write('(LAYER)\n')
        for key in layer:
            gcode_file.write('(' + str(key) + ' , ' + str(layer[key]) + ')\n')
        gcode_file.write('\n')
        
        gcode_file.write('(PROCESS)\n')
        for key in process:
            gcode_file.write('(' + str(key) + ' , ' + str(process[key]) + ')\n')
        gcode_file.write('\n')
        
        gcode_file.write('(TOOL PROFILE)\n')
        for key in tool_profile:
            gcode_file.write('(' + str(key) + ' , ' + str(tool_profile[key]) + ')\n')
        gcode_file.write('\n')
        
        gcode_file.write('(TOOL)\n')
        for key in tool:
            gcode_file.write('(' + str(key) + ' , ' + str(tool[key]) + ')\n')
        gcode_file.write('\n')
        
        gcode_file.write('(PAINT)\n')
        for key in paint_color:
            gcode_file.write('(' + str(key) + ' , ' + str(paint_color[key]) + ')\n')
        gcode_file.write('\n')
        
        # get or dock tool
        if tool_current == None:
            get_tool(tool, tool_change, gcode_file)
            tool_current = tool
        elif tool_current['name'] != tool['name']:
            ln2gcd.water_dip(3, brush_water, tool_current, gcode_file)
            towel = ln2gcd.towel_wipe(2, towel, tool_current, gcode_file)
            dock_tool(tool_current, tool_change, gcode_file)
            get_tool(tool, tool_change, gcode_file)
            tool_current = tool
            
        stroke_line = np.asarray(process_line)
        
        canvas_x_width = canvas['x_max'] - canvas['x_min']
        canvas_y_height = canvas['y_max'] - canvas['y_min']
        
        # center image within canvas; assumes image is smaller than canvas
        canvas_x_min = canvas['x_min'] \
                       + (canvas_x_width - image_prop['x_width'])/2
        canvas_y_min = canvas['y_min'] \
                       + (canvas_y_height - image_prop['y_height'])/2
        
        # translate line points to canvas origin in workspace
        stroke_line += np.asarray([canvas_x_min, canvas_y_min])
        
        palette_brush_map, \
        towel = ln2gcd.stroke_lines_to_paint_gcode(stroke_line,
                                                   palette_brush_map,
                                                   tool_profile,
                                                   tool,
                                                   paint_color,
                                                   brush_palette,
                                                   brush_water,
                                                   towel,
                                                   gcode_file)
        
        gcode_file.write('\n')
    
    # clean tool prior to docking
    ln2gcd.water_dip(3, brush_water, tool, gcode_file)
    towel = ln2gcd.towel_wipe(2, towel, tool, gcode_file)
    
    # dock tool once painting is complete
    dock_tool(tool_current, tool_change, gcode_file)
    
    gcode_file.write('%') # end of gcode file
    gcode_file.close()

def go_to_home(gcode_file):
    # home X and Y, Z (in that order) then set work coordinates

    gcode_file.write('$H\n') # grbl specific homing command
    # set work coordinates
    gcode_file.write('G10 L20 P1 X%.4f Y%.4f Z%.4f A%.4f B%.4f C%.4f\n' 
                     % (0, 0, 0, 0, 0, 0))
    
def get_tool(tool, tool_change, gcode_file):
    # get the tool from it's dock
    
    # raise Z to clearnce height
    gcode_file.write('G00 Z%.4f\n'% tool['z_workspace_clearance'])
    # orient A and C axes
    gcode_file.write('G00 A%.4f C%.4f\n' % (tool_change['a_start'],
                                            tool_change['c_start']))
    # to go tool dock
    gcode_file.write('G00 X%.4f Y%.4f\n' % (tool['x_dock'], tool['y_dock']))
    # plunge into dock
    gcode_file.write('G00 Z%.4f\n' % tool_change['z_dock'])
    
    # change to relative coordinates
    gcode_file.write('G91\n')
    # screw into tool chuck, past overtorque of stepper motor
    gcode_file.write('G00 Z%.4f C%.4f\n' % (-tool_change['z_screw'],
                                            -tool_change['c_screw']))
    # continue to rotate C axis
    gcode_file.write('G00 C%.4f\n' % -60)
    # change to absolute coordinates
    gcode_file.write('G90\n')
    
    # soft set C axis to zero
    gcode_file.write('G10 L20 P1 C%.4f\n' % 0)
    # raise Z to clearnce height
    gcode_file.write('G00 Z%.4f\n' % tool['z_workspace_clearance'])
    
def dock_tool(tool, tool_change, gcode_file):
    # return the tool to it's dock
    
    # raise Z to clearnce height
    gcode_file.write('G00 Z%.4f\n'% tool['z_workspace_clearance'])
    # orient A and C axes
    gcode_file.write('G00 A%.4f C%.4f\n' % (tool_change['a_start'], 
                                            tool_change['c_start']))
    # go to tool dock
    gcode_file.write('G00 X%.4f Y%.4f\n' % (tool['x_dock'], tool['y_dock']))
    # plunge into dock
    gcode_file.write('G00 Z%.4f\n' % (tool_change['z_dock'] - tool_change['z_screw']))
    
    # change to relative coordinates
    gcode_file.write('G91\n')
    # screw into tool chuck, past overtorque of stepper motor
    gcode_file.write('G00 Z%.4f C%.4f\n' % (tool_change['z_screw'], 
                                            tool_change['c_screw']))
    # continue to rotate C axis
    gcode_file.write('G00 C%.4f\n' % 60)
    # change to absolute coordinates
    gcode_file.write('G90\n')
    
    # soft set C axis to zero, 
    # so the C axis doesn't have to rotate to zero prior to picking up the next tool
    gcode_file.write('G10 L20 P1 C%.4f\n' % 0)
    
    # raise Z to clearnce height
    gcode_file.write('G00 Z%.4f\n' % tool['z_workspace_clearance'])
    
if __name__ == '__main__':
    
    with open(os.path.join(DATA_PATH, 'machine_objects.txt'), 'r') as f:
        machine_objects = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'paint_colors.txt'), 'r') as f:
        paint_colors = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'tools.txt'), 'r') as f:
        tools = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'tool_profiles.txt'), 'r') as f:
        tool_profiles = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'layers.txt'), 'r') as f:
        layers = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'processes.txt'), 'r') as f:
        processes = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'process_lines.txt'), 'r') as f:
        process_lines = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'palette_brush_map.txt'), 'r') as f:
        palette_brush_map = json.load(f)
    f.close()
    
    write_brush_gcode('Jackie',
                      machine_objects,
                      paint_colors,
                      tools,
                      tool_profiles,
                      layers,
                      processes,
                      process_lines,
                      palette_brush_map)