
'''
Color boundaries of objects as dictionaries
 - RGBA
 - color_boundaries (RGB -+ 1, no Alpha)
    - np arrays take two BGR ranges
'''
RGBA = {
    "tw_inactive":              [int, int, int, int],
    "sos_tw":                   [int, int, int, int],
    "sos_group":                [int, int, int, int],
    "disconnected_group":       [int, int, int, int],
    "connected_group":          [int, int, int, int],
    "hang_timer":               [int, int, int, int],
    "checkmark":                [int, int, int, int]
}

color_boundaries = {
    "tw_inactive": (list(map(lambda x: x - 1, RGBA["tw_inactive"][:-1])), list(map(lambda x: x + 1, RGBA["tw_inactive"][:-1]))),
    "sos_tw": (list(map(lambda x: x - 1, RGBA["sos_tw"][:-1])), list(map(lambda x: x + 1, RGBA["sos_tw"][:-1]))),
    "sos_group": (list(map(lambda x: x - 1, RGBA["sos_group"][:-1])), list(map(lambda x: x + 1, RGBA["sos_group"][:-1]))),
    "disconnected_group": (list(map(lambda x: x - 1, RGBA["disconnected_group"][:-1])), list(map(lambda x: x + 1, RGBA["disconnected_group"][:-1]))),
    "connected_group": (list(map(lambda x: x - 1, RGBA["connected_group"][:-1])), list(map(lambda x: x + 1, RGBA["connected_group"][:-1]))),
    "hang_timer": (list(map(lambda x: x - 1, RGBA["hang_timer"][:-1])), list(map(lambda x: x + 1, RGBA["hang_timer"][:-1]))),
    "checkmark": ((RGBA["checkmark"][:-1]), list(map(lambda x: x + 1, RGBA["checkmark"][:-1])))
}
