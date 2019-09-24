import numpy as np
import geometry as geom
     
def select_lines(line, 
                 profile_width, 
                 profile_length,
                 select_line_width_overlap, 
                 select_line_length_overlap,
                 select_line_min_length):
    # select longest lines that do not overlap eachother
    # and lines that are longer than the minimum line length
    
    line = np.asarray(line)
    
    profile_width = profile_width*(1 - select_line_width_overlap)
    profile_length = profile_length*(1 - select_line_length_overlap)
    
    line_sorted, \
    corner_sorted = geom.sorted_lines_and_corners(line, 
                                                  profile_width, 
                                                  profile_length)
    
    line_select, \
    corner_select = longest_strokes_no_overlap(line_sorted, corner_sorted)
    
    # this is redundant but needed, length of line is calculated when corners
    # are calculated
    line_length = geom.length_of_line(line_select)
    
    # filter out all lines that are less than the minimum line length
    line_select = np.asarray([x for x, y in zip(line_select, line_length) if y > select_line_min_length])
    
    return line_select

def longest_strokes_no_overlap(line, corner): 
    # determine longest strokes that do not overlap
    
    line_final = []
    corner_final = []
    
    # store stroke start and end points, by selecting strokes 
    # by descending stroke length
    # don't store a stroke if it overlaps a previous longer stroke
    for i in range(len(line)):
        
        # add first line to line evaluation list
        if i == 0:
            line_final.append(line[i])
            corner_final.append(corner[i])

        else:
            
            lines_intersect = False
            
            for j in range(len(corner_final)):
                
                if lines_intersect == True:
                    break
                
                for k in range(4):
                    
                    if k == 3:
                        k_next = 0
                    else:
                        k_next = k + 1
                    
                    for m in range(4):
                        
                        if m == 3:
                            m_next = 0
                        else:
                            m_next = m + 1
                        
                        # if lines of rectangles intersect, then stroke rectangles overlap
                        if geom.lines_intersect(corner[i][k], 
                                                corner[i][k_next], 
                                                corner_final[j][m], 
                                                corner_final[j][m_next]):
                            
                            lines_intersect = True                            
                
            if lines_intersect == False: # lines do not intersect
                
                line_final.append(line[i])
                corner_final.append(corner[i])
    
    line_final = np.asarray(line_final)
    corner_final = np.asarray(corner_final)
    
    return line_final, corner_final

#
#from matplotlib import pyplot as plt
#from matplotlib.collections import LineCollection
#
#line_scan = [[[0, 0], [1, 1]],
#             [[3, 3], [10, 10]],
#             [[1, 0], [5, 4]]]
#
##            [[8, 4], [4, 10]]]
##
##line_scan = np.asarray([[[0,0], [1,0]]])
#
#line_segments = LineCollection(line_scan, linewidths = 2)
#fig, ax = plt.subplots()
#ax.add_collection(line_segments)
#ax.autoscale()
##ax.set_xlim(0, STD_IMAGE_WIDTH)
##ax.set_ylim(0, STD_IMAGE_HEIGHT)
#ax.set_title('line_scan')
#ax.margins(0.1)
#plt.gca().set_aspect('equal', adjustable='box')
#plt.show()
#        
#line_select, \
#corner_select = select_lines(line = line_scan, 
#                             profile_width = 4, 
#                             profile_length = 2, 
#                             line_select_width_overlap = 0, 
#                             line_select_length_overlap = 0)
#
#print('line_select', line_select)
#
#line_segments = LineCollection(line_select, linewidths = 2)
#fig, ax = plt.subplots()
#ax.add_collection(line_segments)
#ax.autoscale()
##ax.set_xlim(0, STD_IMAGE_WIDTH)
##ax.set_ylim(0, STD_IMAGE_HEIGHT)
#ax.set_title('line_select')
#ax.margins(0.1)
#plt.gca().set_aspect('equal', adjustable='box')
#plt.show()
#    