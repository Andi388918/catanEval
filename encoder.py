import numpy as np
import resources

def hexagons_to_string(hexagons):
    hexagons_str = ""
    for hexagon in hexagons:
        hexagons_str += str(hexagon.number)
        hexagons_str += hexagon.resource
    return hexagons_str

def encode(board):
    return board.hexagons_str + board.action_history + str(board.number) + str(board.player.index)