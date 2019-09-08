import os
import json
import numpy as np
import cv2
from definitions import DATA_PATH

def color_quantisize_image(image, color_count):
    # reduce image to a fixed number of colors
    
#    image = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    z = image.reshape((-1, 3))
    z = np.float32(z) #convert image to float32
    
    # define criteria, number of clusters(k) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    compactness, label, centers = cv2.kmeans(z, color_count, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # convert back to unit8 and make original image
    centers = np.uint8(centers)
    image_colorquant = centers[label.flatten()]
    image_colorquant = image_colorquant.reshape((image.shape))
#    image_colorquant = cv2.cvtColor(image_colorquant, cv2.COLOR_LAB2RGB)
    image = image_colorquant
    
    return image, centers
    
if __name__ == '__main__':
    
    COLOR_COUNT = 4
    
    image = cv2.imread(os.path.join(DATA_PATH, 'image_sized.png'))
    
    image_quant, color_center = color_quantisize_image(image, COLOR_COUNT)
    
    cv2.imwrite(os.path.join(DATA_PATH, 'image_quant.png'), image_quant)
    
    # image of each color center
    for i in range(len(color_center)):
        color_mask = cv2.inRange(image_quant, color_center[i], color_center[i])
        image_color = cv2.bitwise_and(image_quant, image_quant, mask = color_mask)
        cv2.imwrite(os.path.join(DATA_PATH, 'color_center_' + str(i) + '.png'), image_color)
    
    # write color_center list to json file
    with open(os.path.join(DATA_PATH, 'image_color_center_bgr.txt'),'w') as f:
        json.dump(color_center.tolist(), f, separators = (',', ':'), sort_keys = True, indent = 4)
    f.close()
    