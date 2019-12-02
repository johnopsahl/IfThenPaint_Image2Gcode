import os
import cv2
import json
from definitions import DATA_PATH

def size_image(image, image_pixel_width, image_pixel_height):
    # size image to max_image_width and max_image_height

    # determine image height and width
    pixel_height, pixel_width = image.shape[:2]

    # if width greater than height, rotate image 270 deg cw
    if pixel_width > pixel_height:
        image = cv2.transpose(image)
        image = cv2.flip(image, 0)

    # resize the image to the pixel width and height
    image = cv2.resize(image, (image_pixel_width, image_pixel_height), interpolation = cv2.INTER_AREA)

    return image

if __name__ == '__main__':

    IMAGE_FILE_NAME = 'jackie_grayscale.png'
    
    with open(os.path.join(DATA_PATH, 'machine_objects.txt'), 'r') as f:
        machine_objects = json.load(f)
    f.close()
    
    machine_object_name_list = [x['name'] for x in machine_objects]
    image_prop_index = machine_object_name_list.index('image_properties')
    image_prop = machine_objects[image_prop_index]
    
    image = cv2.imread(os.path.join(DATA_PATH, IMAGE_FILE_NAME))
    
    image_pixel_width = int(image_prop['x_width']*image_prop['pixel_per_mm'])
    image_pixel_height = int(image_prop['y_height']*image_prop['pixel_per_mm'])
    
    image_sized = size_image(image, 
                             image_pixel_width, 
                             image_pixel_height)
    
    cv2.imwrite(os.path.join(DATA_PATH, 'image_sized.png'), image_sized)
    