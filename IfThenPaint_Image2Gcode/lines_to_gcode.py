import math
import numpy as np
import geometry as geom
                   
def stroke_lines_to_paint_gcode(line, 
                                palette_brush_map,
                                tool_profile,
                                tool,
                                paint_color,
                                canvas,
                                brush_palette, 
                                water, 
                                towel, 
                                gcode_file):
    # generate painterly gcode instructions from the list of lines to paint
      
    a_current = 0
    paint_dist = 0
    clean_dist = 0    
    
    x_start = np.asarray([x[0][0] for x in line])
    y_start = np.asarray([x[0][1] for x in line])
    x_end = np.asarray([x[1][0] for x in line])
    y_end = np.asarray([x[1][1] for x in line])
    
    dy = y_end - y_start
    dx = x_end - x_start
    
    # angle between line and horizontal
    line_angle = np.asarray([geom.atan3(a, b) for a, b in zip(dy, dx)])
    line_length = ((dy)**2 + (dx)**2)**0.5
    
    z_canvas_unload = canvas['z_top'] \
         + tool['length'] \
         - tool['tip_length']*tool_profile['z_canvas_unload_percent']

    z_canvas_retract = canvas['z_top'] + tool['length'] + tool['tip_length']/2
    
    # Z axis to B0C0 clearance height
    gcode_file.write('G00 Z%.4f\n' % tool['z_workspace_clearance'])
    
    for i in range(len(line)):
          
        draw_dist = line_length[i]
        
        x_current = x_start[i]
        y_current = y_start[i]
        
        x_last = x_end[i]
        y_last = y_end[i]
        
        # indicates which move count it is on during processing of a single stroke line
        # multiple moves are needed if brush runs out of paint, brush needs to be cleaned, etc
        paint_move_count = 0
        
        # draw_dist is the total line distance, paint_dist is the length of
        # line distance that can be painted with the quantity of paint currently
        # on the brush 
        
        # loop until line of gcode is complete
        while draw_dist > 0:

            if clean_dist <= 0: # when paint brush drys out, wet and dry brush, dip in paint
                
                # move a axis to nearest equivalent zero location prior 
                # to cleaning, towel wiping, and paint dipping operations
                if tool_profile['a_axial_symmetry'] != 2:
                    a_next = calc_fourth_axis_angle(0, a_current, 0)
                    gcode_file.write('G00 A%.4f\n' % a_next)
                    a_current = a_next
            
                water_dip(4, water, tool, gcode_file)
                towel = towel_wipe(3, towel, tool, gcode_file)
                clean_dist = tool_profile['clean_dist_max']
                    
                palette_brush_map = palette_paint_dip(palette_brush_map,
                                                      paint_color, 
                                                      tool_profile,
                                                      brush_palette,
                                                      tool,
                                                      gcode_file)
                paint_dist = tool_profile['paint_dist_max']
                
            if paint_dist == 0:  # when paint brush runs out of paint, dip in paint
                
                # move a axis nearest equivalent zero location prior to 
                # paint dipping operation
                if tool_profile['a_axial_symmetry'] != 2:
                    a_next = calc_fourth_axis_angle(0, a_current, 0)
                    gcode_file.write('G00 A%.4f\n' % a_next)
                    a_current = a_next
                    
                palette_brush_map = palette_paint_dip(palette_brush_map,
                                                      paint_color,
                                                      tool_profile,
                                                      brush_palette,
                                                      tool,
                                                      gcode_file)
                
                paint_dist = tool_profile['paint_dist_max']
                
            # if it is the first move of the stroke line or the brush was just
            # loaded with paint and the tool doesn't have infinite c axial symmetry
            if (paint_move_count == 0 or paint_dist == tool_profile['paint_dist_max']) \
                and tool_profile['a_axial_symmetry'] != 2:
                a_next = calc_fourth_axis_angle(math.degrees(line_angle[i]), 
                                                a_current,
                                                tool_profile['a_axial_symmetry'])
                gcode_file.write('G00 A%.4f\n' % a_next)
                a_current = a_next
        
            if paint_dist >= draw_dist:
                # paint the entire draw distance
                clean_dist -= draw_dist
                paint_dist -= draw_dist
                draw_dist = 0
                
                gcode_file.write('G00 X%.4f Y%.4f F%i\n' 
                                 % (x_current, 
                                    y_current, 
                                    tool_profile['unload_feed_rate']))
                gcode_file.write('G00 Z%.4f\n' % z_canvas_unload)
                gcode_file.write('G01 X%.4f Y%.4f F%i\n' 
                                 % (x_last, 
                                    y_last, 
                                    tool_profile['unload_feed_rate']))
                gcode_file.write('G00 Z%.4f\n' % z_canvas_retract)
                
                x_current = x_last
                y_current = y_last
                                
            elif paint_dist < draw_dist:
                # paint for the paint distance on the draw distance
                draw_dist -= paint_dist
                clean_dist -= paint_dist
        
                # determine the x and y coordinates when the brush will run out of paint
                x_next = paint_dist*math.cos(line_angle[i]) + x_current
                y_next = paint_dist*math.sin(line_angle[i]) + y_current
                
                gcode_file.write('G00 X%.4f Y%.4f F%i\n' 
                                 % (x_current, 
                                    y_current, 
                                    tool_profile['unload_feed_rate']))
                gcode_file.write('G00 Z%.4f\n' % z_canvas_unload)
                gcode_file.write('G01 X%.4f Y%.4f F%i\n' 
                                 % (x_next, 
                                    y_next, 
                                    tool_profile['unload_feed_rate']))
                gcode_file.write('G00 Z%.4f\n' % z_canvas_retract)
                # all paint on brush has been used
                paint_dist = 0
    
                # set start points of next move as end points of this move
                x_current = x_next
                y_current = y_next
    
            paint_move_count += 1
    
    # move a axis to equivalent zero position
    # prep for next tool profile or tool change
    if tool_profile['a_axial_symmetry'] != 2:
        a_next = calc_fourth_axis_angle(0,
                                        a_current,
                                        tool_profile['a_axial_symmetry'])
        gcode_file.write('G00 A%.4f\n' % a_next)
        a_current = a_next
        
        # soft set A axis to zero
        gcode_file.write('G10 L20 P1 A%.4f\n' % 0)
        
    return palette_brush_map, towel
    
def water_dip(number_of_swirls, water, tool, gcode_file):
    # clean brush during painting to re-wet brush or between colors
    
    z_water_dip = water['z_bottom'] \
                  + tool['length'] \
                  - tool['tip_length']*tool['z_water_dip_percent']
    
    # Z axis to B0C0 clearance height    
    gcode_file.write('G00 Z%.4f\n' % tool['z_workspace_clearance'])
    # move brush to water
    gcode_file.write('G00 X%.4f Y%.4f\n' 
                     % (water['x_center'] + water['dip_radius'], 
                        water['y_center']))
    # lower tool into water
    gcode_file.write('G00 Z%.4f\n' % z_water_dip)
    # dip brush in water in a ccw circle
    for i in range(number_of_swirls):
        
        gcode_file.write('G91\n')
        gcode_file.write('G00 C%.4f\n' % 360)
        gcode_file.write('G90\n')
        
        gcode_file.write('G03 X%.4f Y%.4f I%.4f J%.4f F%i\n'
                         % (water['x_center'] - water['dip_radius'], 
                            water['y_center'],
                            -water['dip_radius'], 
                            0, 
                            water['feed_rate']))
        
        gcode_file.write('G91\n')
        gcode_file.write('G00 C%.4f\n' % -360)
        gcode_file.write('G90\n')
        
        gcode_file.write('G03 X%.4f Y%.4f I%.4f J%.4f  F%i\n'
                         % (water['x_center'] + water['dip_radius'], 
                            water['y_center'],
                            water['dip_radius'], 
                            0,
                            water['feed_rate']))
        
    # Z axis to B0C0 clearance height
    gcode_file.write('G00 Z%.4f\n' % tool['z_workspace_clearance'])

def towel_wipe(number_of_wipes, towel, tool, gcode_file):
    # wipe brush on towel in a ccw motion, the towel is a consumable object
    
    z_towel_wipe = towel['z_top'] \
                   + tool['length'] \
                   - tool['tip_length']*tool['z_towel_wipe_percent']
    
    max_profile_dim = max(tool['profile_width'], tool['profile_length'])
    x_increment = 1.5*max_profile_dim
    
    # Z axis to B0C0 clearance height
    gcode_file.write('G00 Z%.4f\n' % tool['z_workspace_clearance'])
    
    # go to first towel location
    gcode_file.write('G00 X%.4f Y%.4f\n' % (towel['x_current'], 
                                            towel['y_center'] + towel['y_height']/2))
    
    # increase x gap between towel wipe sets
    gcode_file.write('G00 X%.4f\n' % (towel['x_current'] - x_increment))
    
    gcode_file.write('G91\n')
    # rotate A axis by 90 degrees CCW so tool profile oriented correctly
    gcode_file.write('G00 A%.4f\n' % 90)
    gcode_file.write('G90\n')
    
    # lower tool to towel
    gcode_file.write('G00 Z%.4f\n' % z_towel_wipe)
    
    # wipe brush on towel in a ccw motion
    for j in range(number_of_wipes):
        
        # wipe on towel along y axis, negative direction
        gcode_file.write('G01 X%.4f Y%.4f F%i\n' % (towel['x_current'], 
                                                    towel['y_center'] - towel['y_height']/2,
                                                    towel['feed_rate']))
        
        # increment tool over on towel along x axis, negative direction
        gcode_file.write('G01 X%.4f F%i\n' % (towel['x_current'] - x_increment,
                                              towel['feed_rate']))
        
        towel['x_current'] -= x_increment
        
        # wipe on towel along y axis, negative direction
        gcode_file.write('G01 X%.4f Y%.4f F%i\n' % (towel['x_current'], 
                                                    towel['y_center'] + towel['y_height']/2,
                                                    towel['feed_rate']))
        
        # On last wipe, don't incrment tool over on towel along x axis, 
        # negative direction. This leaves unused towel for next towel wipe oepration.
        if j != number_of_wipes - 1:
            # increment tool over on towel along x axis, negative direction
            gcode_file.write('G01 X%.4f F%i\n' % (towel['x_current'] - x_increment,
                                                  towel['feed_rate']))
        
        # advance x_current by x_increment so either same or next brush will
        # start next wiping operation at the correct location
        towel['x_current'] -= x_increment

    # Z axis to B0C0 clearance height
    gcode_file.write('G00 Z%.4f\n' % tool['z_workspace_clearance'])
    
    gcode_file.write('G91\n')
    # rotate A axis by 90 degrees CW to return tool profile to original orientation
    gcode_file.write('G00 A%.4f\n' % -90)
    gcode_file.write('G90\n')
    
    return towel

def palette_paint_dip(palette_brush_map,
                      paint_color, 
                      tool_profile,
                      brush_palette,
                      tool,
                      gcode_file):
    # load tool with paint, paint is a consumable object
    
    # identify bead of paint in palette brush map that matches paint color and
    # tool profile; perhaps there is a way to avoid doing this for every palette
    # paint dip operation
    paint_color_rgb = paint_color['color_rgb']
    tool_profile_name = tool_profile['name']
    
    bead_row_index = 0
    for i in range(len(palette_brush_map)):
        if (palette_brush_map[i]['paint_color_rgb'] == paint_color_rgb and 
            palette_brush_map[i]['tool_profile_name'] == tool_profile_name):
            bead_row_index = i
            break
        
    bead_row = palette_brush_map[bead_row_index]

    y_increment = bead_row['y_increment']
    x_row = bead_row['x_row']
    y_start = bead_row['y_start']
    y_end = bead_row['y_end']
    bead_group_length = bead_row['bead_group_length']
    max_bead_height = bead_row['max_bead_height']
    max_bead_diameter = bead_row['max_bead_diameter']
    
    z_palette_load = brush_palette['z_top'] \
                     + max_bead_height \
                     + tool['length'] \
                     - tool['tip_length']*tool_profile['z_palette_load_percent']
    
    z_palette_retract = brush_palette['z_top'] \
                        + max_bead_height \
                        + tool['length']
    
    gcode_file.write('G00 Z%.4f\n' % tool['z_workspace_clearance'])
    
    for i in range(4):
        
        if i == 0 or i == 3:
            y_position = y_start
        elif i == 1:
            y_position = y_start + 0.25*max_bead_diameter
        elif i == 2:
            y_position = y_start - 0.25*max_bead_diameter
            
        for j in range(2):
            gcode_file.write('G00 X%.4f Y%.4f\n' % (x_row + 0.5*bead_group_length, 
                                                    y_position))
            
            gcode_file.write('G00 Z%.4f\n' % z_palette_load)
        
            gcode_file.write('G01 X%.4f Y%.4f F%i\n' % (x_row - 0.25*bead_group_length, 
                                                        y_position,
                                                        tool_profile['load_feed_rate']))
            
            gcode_file.write('G00 Z%.4f\n' % z_palette_retract)
            
            gcode_file.write('G00 X%.4f Y%.4f\n' % (x_row - 0.5*bead_group_length, 
                                                    y_position))
            
            gcode_file.write('G00 Z%.4f\n' % z_palette_load)
            
            gcode_file.write('G01 X%.4f Y%.4f F%i\n' % (x_row + 0.25*bead_group_length, 
                                                        y_position,
                                                        tool_profile['load_feed_rate']))
            # retract brush
            gcode_file.write('G00 Z%.4f\n' % z_palette_retract)
        
    # Z axis to canvas retract height
    gcode_file.write('G00 Z%.4f\n' % tool['z_workspace_clearance'])

    # check if enough paint bead length for next paint dip, delete from map if not
    if abs(y_end - y_start) - y_increment >= 0.00001: #0.00001 to correct for floating point error
        bead_row['y_start'] -= y_increment
    else:
        del palette_brush_map[bead_row_index]

    return palette_brush_map
    
def calc_fourth_axis_angle(angle_next, angle_current, tool_axial_symmetry):
    # calculate absolute brush angle to be perpendicular to G01 movement
    # angle function input parameters in units of degrees
    
    # tool_axis_symmetry rules
    # 0 -> no axial symmetry, 1 -> 180 deg axial symmetry, 2 -> infinite axial symmetry

    # normalize to a value between 0 and 360 degrees
    norm_angle_next = angle_next % 360
    norm_angle_current = angle_current % 360

    # no symmetry angle change
    angle_change = calc_angle_change(norm_angle_current, norm_angle_next)

    # if tool has 180 degree axial symmetry
    if tool_axial_symmetry == 1:

        # calculate angle change if tool has 180 deg axial symmetry
        angle_change_180 = calc_angle_change((norm_angle_current + 180) % 360, 
                                             norm_angle_next)

        # if 180 deg angle change is less, then use it
        if abs(angle_change_180) < abs(angle_change):
            angle_change = angle_change_180

    # add angle change to current angle for angle change
    angle_next = angle_current + angle_change

    # round to nearest degree; floating point errors accumulate otherwise
    angle_next = round(angle_next)

    return angle_next

def calc_angle_change(angle_start, angle_end):
    # determine which angle to rotate the brush to; normalized 0-360 deg range

    if angle_start > angle_end:
        if angle_start - angle_end < 180:  # small angle; clockwise
            angle_change = -(angle_start - angle_end)
        else:  # large angle; counter clockwise
            angle_change = 360 - (angle_start - angle_end)
    elif angle_start < angle_end:
        if angle_end - angle_start < 180:  # small angle: counter clockwise
            angle_change = angle_end - angle_start
        else:  # large angle; clockwise
            angle_change = -(360 - (angle_end - angle_start))
    else:  # same angle
        angle_change = 0

    return angle_change