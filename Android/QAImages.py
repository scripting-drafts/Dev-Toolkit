import os
from threading import Thread
from Appium_Ops import Appium_Ops
import cv2
import numpy as np
import numexpr as ne
from QAColors import color_boundaries, RGBA


"""
import numpy as np
from robot.libraries.BuiltIn import BuiltIn
from PIL import Image
"""

ROBOT_LIBRARY_VERSION = float
ROBOT_LIBRARY_SCOPE = 'GLOBAL'

def detect_color(path):
    '''
    Each boundary shall be BGR instead of RGB
    # REDACTED

    '''
    
    image = cv2.imread(path)
    image = cv2.resize(image, (0, 0), fx=0.3, fy=0.3)

    for (lower, upper) in color_boundaries.values():
        lower.reverse()
        upper.reverse()

        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")

        mask = cv2.inRange(image, lower, upper)
        output = cv2.bitwise_and(image, image, mask = mask)
	    # show the images
        cv2.imshow("images", np.hstack([image, output]))
        cv2.waitKey(0)

def preprocess_image(path, height, width, proportions_multiplier=0.3):
    '''
    Reads image from path
    Resizes it according to the proportions multiplier
    Cuts the segment of the screen to be processed
    '''
    image = cv2.imread(path)
    actual_height = (height[0] - height[1]) + height[0]
    image = image[actual_height:height[1], width[0]:width[1]]
    image = cv2.resize(image, (0, 0), fx=proportions_multiplier, fy=proportions_multiplier)

    return image

def bincount_numexpr_app(a):
    '''
    Returns the dominant color in the image segment provided
    To be used after preprocess_image
    '''
    a2D = a.reshape(-1, a.shape[-1])
    col_range = (256, 256, 256)  # generically : a2D.max(0)+1
    eval_params = {'a0': a2D[:, 0], 'a1': a2D[:, 1], 'a2': a2D[:, 2],
                   's0': col_range[0], 's1': col_range[1]}
    a1D = ne.evaluate('a0*s0*s1+a1*s0+a2', eval_params)
    img2idx = np.unravel_index(np.bincount(a1D).argmax(), col_range)
    
    return img2idx

def save_img(filename, file):
    cv2.imwrite(filename, file)

def color_difference(color1, color2) -> int:
    """ calculate the difference between two colors as sum of per-channel differences """
    return sum([abs(component1-component2) for component1, component2 in zip(color1, color2)])

def detect_color_in_bounds(path, ui_component, height, width, proportions_multiplier=0.3):
    '''
    Android Client's GUI ui_component possibilities:
    sos, tw_inactive, hang_timer, disconnected_group, connected_group, checkmark

    Compares the dominant color provided by bincount_numexpr_app to a part of the Android Client
    '''
    path = path.replace("/", "\\\\") if Appium_Ops().get_platform()[0].find("Windows") != -1 else path
    
    if os.path.exists(path):
        img = cv2.imread(path)
    else:
        print("Path does not exist:", path)
    
    img = preprocess_image(path, height, width, proportions_multiplier)
    bgr_color = bincount_numexpr_app(img)

    save = Thread(target=save_img, args=(path.split("/")[-1], img))
    save.start()

    rgb_component = [x for x in reversed(list(bgr_color))]
    diff = color_difference(RGBA[ui_component][:-1], rgb_component)

    if diff <= 10:
        print("The color for {} {} {} is aligned with the expected result {}".format(str([i for i, a in locals(
        ).items() if a == ui_component][0]), str(ui_component), rgb_component, RGBA[ui_component][:-1]))
    else:
        raise AssertionError("The color for {} {} {} doesn't fit in the expected range {}".format(str(
            [i for i, a in locals().items() if a == ui_component][0]), str(ui_component), rgb_component, RGBA[ui_component][:-1]))
