import os
import cv2
from definitions import DATA_PATH

def size_image(image, pixel_width_max, pixel_height_max):
    # size image to max_image_width and max_image_height

    # determine image height and width
    pixel_height, pixel_width = image.shape[:2]

    # if width greater than height, rotate image 270 deg cw
    if pixel_width > pixel_height:
        image = cv2.transpose(image)
        image = cv2.flip(image, 0)

    # resize the image to STD_IMAGE_HEIGHT x STD_IMAGE_WIDTH 
    image = cv2.resize(image, (pixel_width_max, pixel_height_max), interpolation = cv2.INTER_AREA)

    return image

if __name__ == '__main__':

    IMAGE_FILE_NAME = 'hillside.jpg'
    
    image = cv2.imread(os.path.join(DATA_PATH, IMAGE_FILE_NAME))
    
    image_sized = size_image(image, 768, 1024)
    
    cv2.imwrite(os.path.join(DATA_PATH, 'image_sized.png'), image_sized)
    