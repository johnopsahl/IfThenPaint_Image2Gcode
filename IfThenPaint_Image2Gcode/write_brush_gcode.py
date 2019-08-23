import os
import json
import numpy as np
import lines_to_gcode as ln2gcd
import datetime
from definitions import DATA_PATH

def write_brush_gcode(project_name,
                      machine_objects,
                      paints,
                      tools,
                      tool_profiles,
                      layers,
                      processes,
                      process_lines,
                      brush_palette_paint_map):
    # generates the gcode file used by the six axis brush cnc machine to 
    # paint on the canvas
    
    timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    
    gcode_file = open(os.path.join(DATA_PATH, str(project_name) + '_brush' + '.gcode'), 'w')
    
    gcode_file.write('%\n') # start of gcode file
    gcode_file.write('\n')
    gcode_file.write('(PROJECT, ' + str(project_name) + ')\n')
    gcode_file.write('(TIMESTAMP, ' + timestamp + ')\n')
    gcode_file.write('\n')
    
    machine_object_name_list = [x['name'] for x in machine_objects]
    canvas_index = machine_object_name_list.index('canvas')
    brush_palette_index = machine_object_name_list.index('brush_palette')
    brush_water_index = machine_object_name_list.index('brush_water')
    towel_index = machine_object_name_list.index('towel')
    tool_change_index = machine_object_name_list.index('tool_change')
    paint_palette_index = machine_object_name_list.index('paint_palette')
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
    
    for paint_bead in brush_palette_paint_map:
        paint_bead['x_position'] += palette_x_offset
        paint_bead['y_start'] += palette_y_offset
        paint_bead['y_end'] += palette_y_offset
        
    # write object parameters to gcode file
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
    for key in towel:
        gcode_file.write('(' + str(key) + ' , ' + str(tool_change[key]) + ')\n')
    gcode_file.write('\n')
    
    tool_current = None 
    
    for layer in layers:          
        
        process_name = layer['process_name']
        tool_profile_name = layer['tool_profile_name']
        paint_name = layer['paint_name']
        
        process_name_list = [x['name'] for x in processes]
        tool_profile_name_list = [x['name'] for x in tool_profiles]
        tool_name_list = [x['name'] for x in tools]
        paint_name_list = [x['name'] for x in paints]
        
        process_index = process_name_list.index(process_name)
        tool_profile_index = tool_profile_name_list.index(tool_profile_name)
        paint_index = paint_name_list.index(paint_name)
        
        process = processes[process_index]
        process_line = process_lines[process_index]
        tool_profile = tool_profiles[tool_profile_index]
        paint = paints[paint_index]
        
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
        for key in paint:
            gcode_file.write('(' + str(key) + ' , ' + str(paint[key]) + ')\n')
        gcode_file.write('\n')
        
        # get or dock tool
        if tool_current == None:
            get_tool(tool, tool_change, gcode_file)
            tool_current = tool
        elif tool_current['name'] != tool['name']:
            dock_tool(tool_current, gcode_file)
            get_tool(tool, tool_change, gcode_file)
            tool_current = tool
            
        stroke_line = np.asarray(process_line)
        
        # translate line points to canvas origin in workspace
        stroke_line += np.asarray([canvas['x_left'], canvas['y_bottom']])
        
        brush_palette_paint_map,
        towel = ln2gcd.stroke_lines_to_paint_gcode(stroke_line,
                                                   tool_profile,
                                                   paint,
                                                   brush_palette_paint_map,
                                                   brush_water,
                                                   towel,
                                                   gcode_file)
        
        gcode_file.write('\n')

    # dock tool once painting is complete
    dock_tool(tool_current, tool_change, gcode_file)
    
    gcode_file.write('%') # end of gcode file
    gcode_file.close()

def get_tool(tool, tool_change, gcode_file):
    # get the specified tool from it's tool dock
    
    # raise Z to clearnce height
    gcode_file.write('G00 Z%.4f\n', tool_change['z_clearance'])
    # to go tool dock
    gcode_file.write('G00 X%.4f Y%.4ff\n' % (tool['x_dock'], tool['y_dock']))
    # orient A and C axes
    gcode_file.write('G00 A%.4f C%.4f\n' % (tool_change['a_start'],
                                            tool_change['c_start']))
    # plunge into dock
    gcode_file.write('G00 Z%.4f\n' % tool_change['z_dock'] + tool_change['z_screw'])
    # screw into tool chuck, past overtorque of stepper motor
    gcode_file.write('G00 Z%.4f C%.4f\n' % (tool_change['z_dock'], -tool_change['c_screw']))
    # soft set C axis to zero
    gcode_file.write('G92 A%.4f\n' % 0)
    # raise Z to clearnce height
    gcode_file.write('G00 Z%.4f\n' % tool_change['z_clearance'])
    
def dock_tool(tool, tool_change, gcode_file):
    # return the tool to it's tool dock
    
    # raise Z to clearnce height
    gcode_file.write('G00 Z%.4f\n', tool_change['z_clearance'])
    # go to tool dock
    gcode_file.write('G00 X%.4f Y%.4f\n' % (tool['x_dock'], tool['y_dock']))
    # orient A and C axes
    gcode_file.write('G00 A%.4f C%.4f\n' % (tool_change['a_start'], 
                                            tool_change['c_start']))
    # plunge into dock
    gcode_file.write('G00 Z%.4f\n' % tool_change['z_dock'])
    # screw into tool chuck, past overtorque of stepper motor
    gcode_file.write('G00 Z%.4f C%.4f\n' % (tool_change['z_dock'] + tool_change['z_screw'], 
                                            tool_change['c_screw']))
    # raise Z to clearnce height
    gcode_file.write('G00 Z%.4f\n' % tool_change['z_clearance'])
    
if __name__ == '__main__':
    
    with open(os.path.join(DATA_PATH, 'machine_objects.txt'), 'r') as f:
        machine_objects = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'paints.txt'), 'r') as f:
        paints = json.load(f)
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
    
    with open(os.path.join(DATA_PATH, 'palette_paint_map.txt'), 'r') as f:
        palette_paint_map = json.load(f)
    f.close()
    
    write_brush_gcode('hill_side',
                      machine_objects,
                      paints,
                      tools,
                      tool_profiles,
                      layers,
                      processes,
                      process_lines,
                      palette_paint_map)