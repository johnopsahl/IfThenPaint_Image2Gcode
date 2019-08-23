import os
import json
import datetime
from definitions import DATA_PATH

def write_paint_gcode(project_name,
                      paint_palette_map,
                      dispenser_paint_volume,
                      machine_objects,
                      paints):
    # generates the gcode file used by the paint management system to 
    # dispense paint on the palette
    
    timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    
    # create gcode file
    gcode_file = open(os.path.join(DATA_PATH, str(project_name) + '_paint' + '.gcode'), 'w')
    
    gcode_file.write('%\n') # start of gcode file
    gcode_file.write('\n')
    gcode_file.write('(PROJECT, ' + str(project_name) + ')\n')
    gcode_file.write('(TIMESTAMP, ' + timestamp + ')\n')
    gcode_file.write('\n')
    
    machine_object_name_list = [x['name'] for x in machine_objects]
    paint_dispenser_index = machine_object_name_list.index('paint_dispenser')
    paint_palette_index = machine_object_name_list.index('paint_palette')
    paint_water_index = machine_object_name_list.index('paint_water')
    paint_dispenser = machine_objects[paint_dispenser_index]
    paint_palette = machine_objects[paint_palette_index]
    paint_water = machine_objects[paint_water_index]
    
    # write paint volumes required to gcode file
    gcode_file.write('(PAINT VOLUME (CM^3) REQUIRED)\n')
    for paint_volume in dispenser_paint_volume:
        for key in paint_volume:
            gcode_file.write('(' + str(key) + ' , ' + str(paint_volume[key]) + ')\n')
        gcode_file.write('\n')
    
    # write object parameters to gcode file
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
    
    remove_from_water(paint_dispenser, gcode_file)
    
    for paint_row in paint_palette_map:          
        
        paint_name = paint_row['paint_name']
        paint_name_list = [x['name'] for x in paints]
        paint_index = paint_name_list.index(paint_name)
        paint = paints[paint_index]
        dispenser_position = paint['dispenser_position']
        
        get_dispenser(dispenser_position, paint_dispenser, gcode_file)
        dispense_paint(paint_row['x_position'],
                       paint_row['y_start'],
                       paint_row['y_end'],
                       paint_dispenser,
                       gcode_file)
        
    return_to_water(paint_water, gcode_file)

    gcode_file.write('%') # end of gcode file
    gcode_file.close()

def get_dispenser(dispenser_position, dispenser, gcode_file):
    # positiion the specificed dispenser under the syringe push plate
    
    dispenser_angle = dispenser_position*dispenser['angle_btw_dispensers']
    
    # raise Z to clearance height
    gcode_file.write('G00 Z%.4f\n' % dispenser['z_clearance'])
    # raise B axis to safe distance
    gcode_file.write('G00 B%.4f\n' % dispenser['b_clearance'])
    # rotate carousel to position dispenser above push plate
    gcode_file.write('G00 A%.4f\n' % dispenser_angle)
    
def dispense_paint(x_position, y_start, y_end, dispenser, gcode_file):
    # dispense paint on the palette
    
    syringe_dispense = dispenser['b_dispense_rate']*(y_start - y_end)
    
    # raise to clearance height
    gcode_file.write('G00 Z%.4f\n' % dispenser['z_clearance'])
    # go to start of paint bead
    gcode_file.write('G00 X%.4f Y%.4f\n' % (x_position, y_start))
    # probe for syringe plunger level, stop when probe switch is activated
    gcode_file.write('G00 B%.4f\n' % dispenser['b_axis_max'])
    # soft set B axis to zero
    gcode_file.write('G92 B%.4f\n' % 0)
    # drop to dispense height
    gcode_file.write('G00 Z%.4f\n' % dispenser['paint_bead_height'])
    # dispense a small amount of paint (to reduce viscosity of thixotropic paint)
    gcode_file.write('G00 B%.4f\n' % dispenser['b_initial_dispense'])
    # dispense bead of paint
    gcode_file.write('G00 X%.4f Y%.4f B%.4f\n' % (x_position, 
                                                  y_end,
                                                  syringe_dispense + dispenser['b_initial_dispense']))
    # raise to clearance height
    gcode_file.write('G00 Z%.4f\n' % dispenser['z_clearance'])

def remove_from_water(dispenser, gcode_file):
    # remove syringe carousel from the paint water dish
    
    # raise to clearance height
    gcode_file.write('G00 Z%.4f\n' % dispenser['z_clearance'])
    # jostle dispensers to reomve any water droplets
    gcode_file.write('G00 A%.4f\n' % 90)
    gcode_file.write('G00 A%.4f\n' % -90)
    gcode_file.write('G00 A%.4f\n' % 0)
    
def return_to_water(paint_water, gcode_file):
    # return paint carousel to the paint water dish, so the tips of the
    # syringes do not dry out 
    
    # go to water
    gcode_file.write('G00 X%.4f Y%.4f\n' % (paint_water['x_center'],
                                            paint_water['y_center']))
    # lower dispensers into water
    gcode_file.write('G00 Z%.4f\n' % paint_water['z_top'])
    
if __name__ == '__main__':
    
    with open(os.path.join(DATA_PATH, 'palette_paint_map.txt'), 'r') as f:
        paint_palette_map = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'dispenser_paint_volume.txt'), 'r') as f:
        dispenser_paint_volume = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'machine_objects.txt'), 'r') as f:
        machine_objects = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'paints.txt'), 'r') as f:
        paints = json.load(f)
    f.close()
    
    write_paint_gcode('hill_side',
                      paint_palette_map,
                      dispenser_paint_volume,
                      machine_objects,
                      paints)