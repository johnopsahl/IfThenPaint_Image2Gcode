import os
import json
import datetime
from definitions import DATA_PATH

def write_paint_gcode(project_name,
                      palette_paint_map,
                      machine_objects,
                      paints):
    # generates the gcode file used by the paint management system to 
    # dispense paint on the palette
    
    timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    
    # create gcode file
    gcode_file = open(os.path.join(DATA_PATH, str(project_name) + '_paint' + '.gcode'), 'w')
    
    gcode_file.write('%\n') # start of gcode file
    gcode_file.write('(PROJECT, ' + str(project_name) + ')\n')
    gcode_file.write('(TIMESTAMP, ' + timestamp + ')\n')
    gcode_file.write('\n')
    
    machine_object_name_list = [x['name'] for x in machine_objects]
    paint_management_index = machine_object_name_list.index('paint_management')
    paint_dispenser_index = machine_object_name_list.index('paint_dispenser')
    paint_palette_index = machine_object_name_list.index('paint_palette')
    paint_water_index = machine_object_name_list.index('paint_water')
    paint_management = machine_objects[paint_management_index]
    paint_dispenser = machine_objects[paint_dispenser_index]
    paint_palette = machine_objects[paint_palette_index]
    paint_water = machine_objects[paint_water_index]
    
    # write paint volumes required to gcode file
#    gcode_file.write('(PAINT VOLUME CM^3 REQUIRED)\n')
#    for paint_volume in dispense_paint_volume:
#        for key in paint_volume:
#            gcode_file.write('(' + str(key) + ' , ' + str(paint_volume[key]) + ')\n')
#        gcode_file.write('\n')

    # write object parameters to gcode file
    gcode_file.write('(PAINT MANAGEMENT)\n')
    for key in paint_management:
        gcode_file.write('(' + str(key) + ' , ' + str(paint_management[key]) + ')\n')
    gcode_file.write('\n')
    
    gcode_file.write('(PAINT DISPENSER)\n')
    for key in paint_dispenser:
        gcode_file.write('(' + str(key) + ' , ' + str(paint_dispenser[key]) + ')\n')
    gcode_file.write('\n')
    
    gcode_file.write('(PAINT PALETTE)\n')
    for key in paint_palette:
        gcode_file.write('(' + str(key) + ' , ' + str(paint_palette[key]) + ')\n')
    gcode_file.write('\n')
    
    gcode_file.write('(PAINT WATER)\n')
    for key in paint_water:
        gcode_file.write('(' + str(key) + ' , ' + str(paint_water[key]) + ')\n')
    gcode_file.write('\n')
    
    gcode_file.write('G17 G21 G90 G94 G54\n') # initialization block
    # G17 -> G02 and G03 commands about the XY plane
    # G21 -> units of millimeters
    # G90 -> absolute coordinates
    # 694 -> feed rate in distance/minute units
    # G54 -> workspace coordinates
        
    go_to_water_z_clearance(paint_water, gcode_file)
    go_to_home(paint_management, gcode_file)
    
    for paint_row in palette_paint_map:          
        
        paint_color_rgb = paint_row['paint_color_rgb']
        paint_name_list = [x['color_rgb'] for x in stock_paints]
        paint_index = paint_name_list.index(paint_color_rgb)
        paint = paints[paint_index]
        dispenser_position = paint['position']
        
        get_dispenser(dispenser_position, 
                      paint_dispenser, 
                      paint_palette, 
                      gcode_file)
        
        dispense_paint(paint_row,
                       paint_dispenser,
                       paint_management,
                       paint_palette,
                       gcode_file)
    
    # go to 0 position of A axis prior to returning to water
    get_dispenser(0, paint_dispenser, paint_palette, gcode_file)
    
    return_to_water(paint_water, gcode_file)
    palette_to_workspace(paint_management, gcode_file)
    
    gcode_file.write('%') # end of gcode file
    gcode_file.close()

def get_dispenser(dispenser_position, dispenser, palette, gcode_file):
    # positiion the specificed dispenser under the syringe push plate
    
    dispenser_angle = dispenser_position*dispenser['angle_btw_dispensers']
    
    # raise to palette clearance height
    gcode_file.write('G00 Z%.4f\n' % (dispenser['z_clearance'] +
                                      palette['z_top']))
    # raise B axis to safe distance
    gcode_file.write('G00 B%.4f\n' % dispenser['b_clearance'])
    # rotate carousel to position dispenser above push plate
    gcode_file.write('G00 A%.4f\n' % dispenser_angle)
    
def dispense_paint(paint_row, 
                   dispenser, 
                   paint_management, 
                   palette, 
                   gcode_file):
    # dispense paint on the palette
    
    y_increment = paint_row['y_increment']
    y_end = paint_row['y_end']
    y_current = paint_row['y_start']
    
    # raise to palette clearance height
    gcode_file.write('G00 Z%.4f\n' % (dispenser['z_clearance'] +
                                      palette['z_top']))
    # go to start of paint bead
    gcode_file.write('G00 X%.4f Y%.4f\n' % (paint_row['x_row'], y_current))
    
    # go to dispense height
    gcode_file.write('G00 Z%.4f\n' % (paint_row['bead_height'] + 
                                      palette['z_top']))
    
    # probe for syringe plunger level, stop when probe switch is activated
    gcode_file.write('G38.3 B%.4f F%.4f\n' % (paint_management['b_max_travel'],
                                              dispenser['b_probe_feedrate']))
    
    # change to relative coordinates
    gcode_file.write('G91\n')
    
    # initial b travel to make up for distance between top of paint syringe
    # plunger and bottom of push plate when b probe switch has been activated
    gcode_file.write('G01 B%.4f\n' % paint_management['b_switch_initial'])
    
    while y_current >= y_end:
        
        # dispense paint
        gcode_file.write('G01 B%.4f F%.4f\n' % (paint_row['plunger_dist'], 
                                                dispenser['dispense_feedrate']))
        # pause for paint response
        gcode_file.write('G04 P%.4f\n' % dispenser['dispense_delay'])
        
        # if not the last dispense
        if y_current - y_increment >= y_end:
            # move to next paint bead
            gcode_file.write('G00 Y%.4f\n' % -y_increment)
        
        y_current -= y_increment
        
    # raise push plate limit off of syringe plunger so it is no longer activated
    gcode_file.write('G00 B%.4f\n' % -dispenser['b_probe_retract'])
    
    # change back to absolute coordinates
    gcode_file.write('G90\n')
    
    # raise to palette clearance height
    gcode_file.write('G00 Z%.4f\n' % (dispenser['z_clearance']+
                                      palette['z_top']))

def go_to_water_z_clearance(paint_water, gcode_file):
    # remove syringe carousel from the paint water dish
    
    # change to relative coordinates
    gcode_file.write('G91\n')
    # raise to clearance height
    gcode_file.write('G00 Z%.4f\n' % paint_water['z_clearance'])
    # return to absolute coordinates
    gcode_file.write('G90\n')
    
def return_to_water(paint_water, gcode_file):
    # return paint carousel to the paint water dish, so the tips of the
    # syringes do not dry out 
    
    # go to water
    gcode_file.write('G00 Y%.4f\n' % paint_water['y_water'])
    # lower dispensers into water
    gcode_file.write('G00 Z%.4f\n' % paint_water['z_water'])
    
def go_to_home(paint_management, gcode_file):
    # home X and Y, Z, and B axes (in that order) then set work coordinates
    
    # short pause so the machine can go into idle state
    gcode_file.write('G04 P%.4f\n' % 0.5) 
    gcode_file.write('$H\n') # grbl specific homing command
    # set work coordinates
    gcode_file.write('G10 L20 P1 X%.4f Y%.4f Z%.4f A%.4f B%.4f\n' 
                     % (0, paint_management['y_max_travel'], 0, 0, 0))
    
def palette_to_workspace(paint_management, gcode_file):
    # move palette to workspace
    
    gcode_file.write('G00 X%.4f\n' % paint_management['x_workspace'])
    
if __name__ == '__main__':
    
    with open(os.path.join(DATA_PATH, 'palette_paint_map.txt'), 'r') as f:
        palette_paint_map = json.load(f)
    f.close()
    
#    with open(os.path.join(DATA_PATH, 'dispense_paint_volume.txt'), 'r') as f:
#        dispense_paint_volume = json.load(f)
#    f.close()
    
    with open(os.path.join(DATA_PATH, 'machine_objects.txt'), 'r') as f:
        machine_objects = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'stock_paints.txt'), 'r') as f:
        stock_paints = json.load(f)
    f.close()
    
    write_paint_gcode('hello_world',
                      palette_paint_map,
                      machine_objects,
                      stock_paints)