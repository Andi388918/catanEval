import pickle
import os

path = os.path.dirname(os.path.realpath(__file__))

def load_board_save():
    with open(os.path.join(path, 'board_save/board.pkl'), 'rb') as input:
        board_save = pickle.load(input)
    return board_save

def save_board(settlement_places, road_places, hexagons):
    with open(os.path.join(path, 'board_save/board.pkl'), 'wb') as output:
        pickle.dump((settlement_places, road_places, hexagons), output, pickle.HIGHEST_PROTOCOL)
