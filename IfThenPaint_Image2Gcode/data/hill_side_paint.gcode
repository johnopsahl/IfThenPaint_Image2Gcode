%

(PROJECT, hill_side)
(TIMESTAMP, 2019-08-25T13:51:58)

(PAINT VOLUME (CM^3) REQUIRED)
(paint_name , black)
(paint_volume , 0.16000000000000003)

(PAINT DISPENSER)
(angle_btw_dispensers , 36)
(b_dispense_rate , 1.6666666666666667)
(z_dispense , 3)
(x_bead_offset , 10)
(z_clearance , 10)
(b_initial_dispense , 0.75)
(b_axis_max , 30)
(paint_bead_width , 4)
(paint_bead_height , 2)
(b_clearance , 5)
(name , paint_dispenser)

(PAINT PALETTE)
(y_min , 0)
(y_max , 200)
(name , paint_palette)
(x_min , 0)
(x_max , 100)
(z_top , 2)

(PAINT WATER)
(z_top , -62)
(y_center , -45.25)
(name , paint_water)
(x_center , 164)

G00 Z10.0000
G00 A90.0000
G00 A-90.0000
G00 A0.0000
G00 Z10.0000
G00 B5.0000
G00 A144.0000
G00 Z10.0000
G00 X95.0000 Y200.0000
G00 B30.0000
G92 B0.0000
G00 Z2.0000
G00 B0.7500
G00 X95.0000 Y180.0000 B34.0833
G00 Z10.0000
G00 X164.0000 Y-45.2500
G00 Z-62.0000
%