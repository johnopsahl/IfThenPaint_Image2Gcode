import numpy as np
import cv2

def random_non_matching_color(colors):
    # a random color that does not match any of the input colors
    
    # if colors contains all the colors, return false, just for fun
    if len(colors) > (256*256*256):
        return False
    
    no_match_count = 0
    
    while no_match_count != len(colors):
    
        no_match_count = 0
        
        r = np.random.randint(0, 255)
        g = np.random.randint(0, 255)
        b = np.random.randint(0, 255)
        
        for i in range(len(colors)):
            if colors[i][0] != r and \
               colors[i][1] != g and \
               colors[i][2] != b:
                   no_match_count += 1
    
    random_color = [r, g, b]
    
    return random_color

def color_polygon(image, corner, color_bgr):
    
    image_height, image_width = image.shape[:2]
    
    corner = (np.asarray([0, image_height]) - corner)*np.asarray([-1, 1])
    cv2.fillPoly(image, np.int32(corner), color_bgr)

    return image
        
        
        
        
        