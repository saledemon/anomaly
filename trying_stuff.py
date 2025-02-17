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
    0: "s_outer.png",
    1: "s_middle.png",
    2: "s_inner.png"
}

hot_points = {
    0: (300, 70), # outer ring
    1: (650, 70),
    2: (650, 930),
    3: (300, 920),
    4: (375, 195), # middle ring
    5: (780, 370),
    6: (375, 795),
    7: (200, 370),
    8: (350, 335), # inner ring
    9: (630, 335),
    10: (630, 655),
    11: (350, 655),
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