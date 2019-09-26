import geometry as geom
import numpy as np

def set_line_max_length(lines, 
                        line_max_length):
    # reduce lines longer than the line max length into multiple lines of 
    # less than or equal length as the line max length
    
    line_length = geom.length_of_line(lines)
    line_angle = geom.angle_of_line(lines)
    
    lines_modified = []
    
    for i in range(len(lines)):
        
        if line_length[i] > line_max_length:
            
            line_length_temp = line_length[i]
            x_start = lines[i][0][0]
            y_start = lines[i][0][1]
            
            while line_length_temp > 0:
                
                if line_length_temp > line_max_length:
                    x_end = x_start + line_max_length*np.cos(line_angle[i])
                    y_end = y_start + line_max_length*np.sin(line_angle[i])
                    lines_modified.append([[x_start, y_start], [x_end, y_end]])
                    line_length_temp -= line_max_length
                    x_start = x_end
                    y_start = y_end
                    
                else: #line_length_temp <= line_max_length
                    x_end = lines[i][1][0]
                    y_end = lines[i][1][1]
                    lines_modified.append([[x_start, y_start], [x_end, y_end]])
                    line_length_temp = 0
                    
        else:
            lines_modified.append(lines[i])
        
    lines_modified = np.asarray(lines_modified)
        
    return lines_modified

if __name__ == '__main__':
    
    lines = np.asarray([[[0, 0], [-1, 1]], [[0, 0], [1, -1]]])
    
    lines_modified = set_line_max_length(lines, 1)
    
    print(lines_modified)
