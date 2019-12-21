# IfThenPaint_Image2Gcode
Create cnc painting machine g-code from bitmap images.

[If () Then {Paint} Project](https://hackaday.io/project/166524-if-then-paint)
 
Script run sequence:
1. add_image_properties
2. size_image
3. quantisize_image
4. add_tools
5. add_tool_profiles
6. add_stock_paints
7. add_paint_colors
8. add_machine_objects
9. line_scan
10. commit_process/remove_process
11. add_layer
12. create_painting_preview
13. layer_paint_dips
14. map_palette
15. write_brush_gcode 
16. write_paint_gcode
