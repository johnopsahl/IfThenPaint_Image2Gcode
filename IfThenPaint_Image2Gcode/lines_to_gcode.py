import math
import numpy as np
import geometry as geom
                   
def stroke_lines_to_paint_gcode(line, 
                                tool_profile,
                                tool,
                                paint, 
                                brush_palette_paint_map, 
                                water, 
                                towel, 
                                gcode_file):
    # generate painterly gcode instructions from the list of lines to paint
      
    a_start = 0
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
    
    # Z axis to B0C0 clearance height
    gcode_file.write('G00 Z%.4f\n' % tool['z_B0C0_clearance'])
    
    for i in range(len(line)):
          
        draw_dist = line_length[i]
    
        x_current = x_start[i]
        y_current = y_start[i]
        
        x_next = x_end[i]
        y_next = y_end[i]
        
        x_last = x_end[i]
        y_last = y_end[i]
        
        # indicates which move count it is on during processing of a single stroke line
        # multiple moves are needed if brush runs out of paint, brush needs to be cleaned, etc
        paint_move_count = 0
        
        # loop until line of gcode is complete
        while draw_dist > 0:

            if clean_dist <= 0: # when paint brush drys out, wet and dry brush, dip in paint
                water_dip(3, water, tool, gcode_file)
                towel = towel_wipe(2, towel, tool, gcode_file)
                clean_dist = tool_profile['clean_dist_max']
                brush_palette_paint_map = palette_paint_dip(2, 
                                                            brush_palette_paint_map,
                                                            paint, tool_profile, 
                                                            gcode_file)
                paint_dist = tool_profile['paint_dist_max']
                
            if paint_dist == 0:  # when paint brush runs out of paint, dip in paint
                brush_palette_paint_map = palette_paint_dip(2, 
                                                            brush_palette_paint_map,
                                                            paint, tool_profile, 
                                                            gcode_file)
                paint_dist = tool_profile['paint_dist_max']
                
            # if it is the first move of the stroke line and the tool doesn't have infinite c axial symmetry
            if paint_move_count == 0 and tool_profile['c_axial_symmetry'] != 2:
                a_last = calc_fourth_axis_angle(line_angle[i], a_start,
                                                tool_profile['c_axial_symmetry'])
                a_start = a_last
                gcode_file.write('G00 A%.4f C%.4f\n' 
                                 % (a_last, tool_profile['c_angle']))
    
#              ****************************************************
#              define custom a axis movements here
#             if paint_move_count == 0:
#                 if a_end == 0:
#                     a_end = 60
#                 elif a_end == 60:
#                     a_end = 120
#                 elif a_end == 120:
#                     a_end = 60
#            
#                 paint_gcode_file.write('G0 A%.15f\n' % a_end)
#              ***************************************************
    
            if paint_dist >= draw_dist:
                # paint the entire draw distance
                clean_dist -= draw_dist
                paint_dist -= draw_dist
                draw_dist = 0
                
                gcode_file.write('G00 X%.4f Y%.4f F%i\n' 
                                 % (x_current, y_current, tool_profile['feed_rate']))
                gcode_file.write('G00 Z%.4f\n' % tool_profile['z_canvas_paint'])
                gcode_file.write('G01 X%.4f Y%.4f F%i\n' 
                                 % (x_last, y_last, tool_profile['feed_rate']))
                gcode_file.write('G00 Z%.4f\n' % tool_profile['z_canvas_retract'])
                
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
                                 % (x_current, y_current, tool_profile['feed_rate']))
                gcode_file.write('G00 Z%.4f\n' % tool_profile['z_canvas_paint'])
                gcode_file.write('G01 X%.4f Y%.4f F%i\n' 
                                 % (x_next, y_next, tool_profile['feed_rate']))
                gcode_file.write('G00 Z%.4f\n' % tool_profile['z_canvas_retract'])
                # all paint on brush has been used
                paint_dist = 0
    
                # set start points of next move as end points of this move
                x_current = x_next
                y_current = y_next
    
            paint_move_count += 1
        
    return brush_palette_paint_map, towel
    
def water_dip(number_of_swirls, water, tool, gcode_file):
    # clean brush during painting to re-wet brush or between colors
    
    # Z axis to B0C0 clearance height    
    gcode_file.write('G00 Z%.4f\n' % tool['z_B0C0_clearance'])
    # move brush to water
    gcode_file.write('G00 X%.4f Y%.4f\n' 
                     % (water['x_center'] + water['dip_radius'], water['y_center']))
    # lower tool into water
    gcode_file.write('G00 Z%.4f\n' % tool['z_water_dip'])
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
    gcode_file.write('G00 Z%.4f\n' % tool['z_B0C0_clearance'])

def towel_wipe(number_of_wipes, towel, tool, gcode_file):
    # wipe brush on towel in a ccw motion, the towel is a consumable object
    
    # Z axis to B0C0 clearance height
    gcode_file.write('G00 Z%.4f\n' % tool['z_B0C0_clearance'])
           
    # wipe brush on towel in a ccw motion
    for j in range(number_of_wipes):
        
        # go to towel
        gcode_file.write('G00 X%.4f Y%.4f\n' % (towel['x_current'], towel['y_center']))
        # lower tool to towel
        gcode_file.write('G00 Z%.4f\n' % tool['z_towel_wipe'])
        
        gcode_file.write('G03 X%.4f Y%.4f I%.4f J%.4f F%i\n'
                         % (towel['x_current'], 
                            towel['y_center'], 
                            -towel['wipe_radius'], 
                            0, 
                            towel['feed_rate']))

        # increment towel x position so a different part of the towel is used next
        towel['x_current'] -= towel['x_increment']

    # Z axis to B0C0 clearance height
    gcode_file.write('G00 Z%.4f\n' % tool['z_B0C0_clearance'])
    
    return towel

def palette_paint_dip(number_of_dips, 
                      brush_palette_paint_map, 
                      paint, 
                      tool_profile, 
                      gcode_file):
    # load tool with paint, paint is a consumable object
    
    # identify bead of paint in palette paint map that matches paint color and
    # tool profile
    paint_color_rgb = paint['color_rgb']
    tool_profile_name = tool_profile['name']
    for i in range(len(brush_palette_paint_map)):
        if (brush_palette_paint_map[i]['paint_color_rgb'] == paint_color_rgb and 
            brush_palette_paint_map[i]['tool_profile_name'] == tool_profile_name):
            paint_bead_index = i
            break
        
    paint_bead = brush_palette_paint_map[paint_bead_index]
    
    x_position = paint_bead['x_position']
    y_start = paint_bead['y_start']
    y_end = paint_bead['y_end']
    paint_bead_length = tool_profile['paint_bead_length']
           
    # Z axis to canvas retract height
    gcode_file.write('G00 Z%.4f\n' % tool_profile['z_canvas_retract'])

    # go to paint bead dip location
    gcode_file.write('G00 X%.4f Y%.4f\n' % (x_position,
                                            y_start - paint_bead_length/2))
    
    for i in range(number_of_dips):
        # dip brush into paint
        gcode_file.write('G00 Z%.4f\n' % tool_profile['z_paint_dip'])
        # Z axis to canvas retract height
        gcode_file.write('G00 Z%.4f\n' % tool_profile['z_palette_retract'])
    
    # Z axis to canvas retract height
    gcode_file.write('G00 Z%.4f\n' % tool_profile['z_canvas_retract'])
    
    # check if enough paint bead length for next paint dip, delete from map if not
    if ((y_start - y_end) - paint_bead_length) >= paint_bead_length:
        brush_palette_paint_map[paint_bead_index]['y_start'] -= paint_bead_length
    else:
        del brush_palette_paint_map[paint_bead_index]

    return brush_palette_paint_map
        
## paint dip operation for paint bins
#def paint_dip(number_of_dips, paint, tool_profile, gcode_file):
#        
#    random_radius = np.random.random()*paint.dip_radius
#    random_angle = np.random.random()*(2*math.pi)
#
#    x_temp = random_radius*math.cos(random_angle) + paint.x_center
#    y_temp = random_radius*math.sin(random_angle) + paint.y_center
#
#    # dip brush in paint
#    gcode_file.write('G00 X%.4f Y%.4f\n' % (x_temp, y_temp))
#
#    for i in range(number_of_dips):
#        gcode_file.write('G00 Z%.4f\n' % paint.z_dip)
#        gcode_file.write('G00 Z%.4f\n' % tool_profile.z_canvas_retract)   
    
def calc_fourth_axis_angle(path_angle, angle_current, tool_axial_symmetry):
    # calculate absolute brush angle to be perpendicular to G01 movement
    
    # tool_axis_symmetry rules
    # 0 -> no axial symmetry, 1 -> 180 deg axial symmetry, 2 -> infinite axial symmetry
    
    # angle between vector and horizontal
    norm_angle_end = math.degrees(path_angle)

    # normalize the start angle to a value between 0 and 360 degrees
    norm_angle_current = angle_current % 360

    # no symmetry angle change
    angle_change = calc_angle_change(norm_angle_current, norm_angle_end)

    # if tool has 180 degree axial symmetry
    if tool_axial_symmetry == 1:

        # calculate angle change if tool has 180 deg axial symmetry
        angle_change_180 = calc_angle_change((norm_angle_current + 180) % 360, 
                                             norm_angle_end)

        # if 180 deg angle change is less, then use it
        if abs(angle_change_180) < abs(angle_change):
            angle_change = angle_change_180

    # add angle change to current angle for angle change
    angle_next = angle_current + angle_change

    # round to nearest degree; floating point errors occur otherwise
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