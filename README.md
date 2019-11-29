# IfThenPaint_Image2Gcode
Create cnc painting machine g-code from bitmap images.

Script run sequence:
1. size_image
2. quantisize_image
3. add_tools
4. add_tool_profiles
5. add_stock_paints
6. add_paint_colors
7. add_machine_objects
8. line_scan
9. commit_process/remove_process
10. add_layer
11. create_painting_preview
12. layer_paint_dips
13. map_palette
14. write_brush_gcode 
15. write_paint_gcode
