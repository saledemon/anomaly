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

def is_adjacent(zone_id, target):
    return target in board_repr[zone_id]