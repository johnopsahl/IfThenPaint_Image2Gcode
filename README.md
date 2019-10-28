# IfThenPaint_Image2Gcode
Create cnc painting machine g-code from bitmap images.

Script run sequence:
1. size_image
2. quantisize_image
3. add_tools
4. add_tool_profiles
5. add_stock_paints
6. add_machine_objects
7. line_scan
8. commit_process/remove_process
9. add_layer
10. create_painting_preview
11. layer_painting_distance
12. palette_paint_map
13. write_brush_gcode 
14. write_paint_gcode
