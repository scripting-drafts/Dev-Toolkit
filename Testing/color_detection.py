from QAImages import detect_color_in_bounds
from Appium_Ops import Appium_Ops
import os
platform = Appium_Ops().get_platform()[0]
separator = "\\" if platform.find("Windows") != -1 else "/"
path = os.getcwd()
path = "{}{}0-current_sos_rx.png".format(path, separator)
print(path)
# detect_color(path)
asd = detect_color_in_bounds(path, "disconnected_group", [int, int], [int, int])
print(asd)
