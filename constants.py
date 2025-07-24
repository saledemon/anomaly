from PyQt5.QtGui import QPixmap, QTransform, QImage

PLAYABLE_ZONES = [n for n in range(12)]

board_repr = {
    0: [1, 3, 4, 7], # outer ring
    1: [0, 2, 4, 5],
    2: [1, 3, 5, 6],
    3: [0, 2, 6, 7],
    4: [0, 1, 8, 9], # middle ring
    5: [1, 2, 9, 10],
    6: [2, 3, 10, 11],
    7: [0, 3, 8, 11],
    8: [4, 7, 9, 11], # inner ring
    9: [4, 5, 8, 10],
    10: [5, 6, 9, 11],
    11: [6, 7, 8, 10],
    12: [0], # shuttle bay
    13: [1],
    14: [2],
    15: [3],
    16: [8, 9, 10, 11] # reactor
}

TELEPORT_RANGE = [-1]
INFINITE_RANGE = [3]

def get_zones_in_range(zid, zrange: list):
    zones = []

    if zrange == TELEPORT_RANGE:
        return [z for z in PLAYABLE_ZONES if z != zid]

    if 3 in zrange: # if range is 3, then return all PLAYABLE_ZONES
        return PLAYABLE_ZONES

    if 0 in zrange:
        zones.append(zid)

    if 1 in zrange:
        zones.extend(board_repr[zid])

    if 2 in zrange:
        for z in board_repr[zid]:
            zones.extend(board_repr[z])

    zones = list(set(zones))

    if 0 not in zrange and zid in zones: # range 2 might have added current zone, so remove it if necessary (for Stims)
        zones.remove(zid)

    return zones

opposite_board_zones = {
    0: 2, # outer ring
    1: 3,
    2: 0,
    3: 1,
    4: 6, # middle ring
    5: 7,
    6: 4,
    7: 5,
    8: 10, # inner ring
    9: 11,
    10: 8,
    11: 9,
}

def is_move_valid(current_zone, target_zone):
    if current_zone == -1:
        return False
    return target_zone in board_repr[current_zone]

board_placement = [
    (0, 0), # outer ring
    (500.37, 0),
    (500.37, 500.37),
    (0, 500.37),
    (300.18, 100.02), # middle ring
    (717.1, 300.18),
    (300.18, 717.1),
    (100.02, 300.18),
    (250.26, 250.26), # inner ring
    (500.34, 250.26),
    (500.34, 500.34),
    (250.26, 500.34),
    (153.62, 153.62), # shuttle bays
    (625.5, 153.62),
    (625.5, 625.5),
    (153.62, 625.5),
    (366.62, 366.62), # reactor
]

"""
Outer Ring = 0
Middle Ring = 1
Inner Ring = 2

White Square = 3
Turquoise Square = 4
Purple Square = 5
Yellow Square = 6

Pink Triangle = 7
Brown Triangle = 8
"""

sym_map = {
    0: QImage("res/s_outer.png"),
    1: QImage("res/s_middle.png"),
    2: QImage("res/s_inner.png"),
    3: QImage("res/s_square1.png"),
    4: QImage("res/s_square2.png"),
    5: QImage("res/s_square3.png"),
    6: QImage("res/s_square4.png"),
    7: QImage("res/s_tri1.png"),
    8: QImage("res/s_tri2.png"),
}

hot_points = {
    0: (204.85257409985255, 172.01361183957084),
    1: (828.7928570452049, 193.9062533464253),
    2: (835.0478974757348, 814.7190160765127),
    3: (186.08745280826298, 827.2290969375724),
    4: (498.8394743347554, 178.2686522701007),
    5: (816.2827761841452, 498.8394743347554),
    6: (501.96699455002033, 827.2290969375724),
    7: (173.5773719472033, 501.96699455002033),
    8: (376.86618593942336, 386.24874658521816),
    9: (619.249002622455, 387.8125066928506),
    10: (633.3228435911471, 617.6852425148226),
    11: (384.68498647758565, 619.249002622455),
    12: None,
    13: None,
    14: None,
    15: None,
    16: (500, 500)
}



board_sym = {
    0: [0, 3, 6], # outer ring
    1: [0, 3, 4],
    2: [0, 4, 5],
    3: [0, 5, 6],
    4: [1, 3, 7], # middle ring
    5: [1, 4, 7],
    6: [1, 5, 8],
    7: [1, 6, 8],
    8: [2, 3, 7], # inner ring
    9: [2, 4, 7],
    10: [2, 5, 8],
    11: [2, 6, 8]
}

def is_adjacent(zone_id, target):
    return target in board_repr[zone_id]