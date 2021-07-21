from board import Board
import random
import drawing
import time
import pygame
from encoder import encode
import math
import evaluation

def play_games(games = 100, print_every = False, draw = False):
    s = time.time()
    steps = 0

    for i in range(games):
        if print_every and i % print_every == 0:
            print(i)
        won = False
        board = Board()

        evaluations = {}

        for settlement_place1 in board.settlement_places:
            evaluations[settlement_place1] = {}
            for settlement_place2 in board.settlement_places:
                if settlement_place1 != settlement_place2 and settlement_place2 not in settlement_place1.settlement_neighbours:
                    if "fisch" in [x.resource for x in settlement_place1.bordersOn] and "fisch" in [x.resource for x in settlement_place2.bordersOn]:
                        pass
                    else:
                        income, trades = evaluation.join_evaluate([settlement_place1, settlement_place2])
                        eval = evaluation.evaluate(income, trades)

                        evaluations[settlement_place1][settlement_place2] = eval

        for settlement_place, eval in evaluations.items():
            evaluations[settlement_place] = {k: v for k, v in sorted(eval.items(), key=lambda item: item[1])}
            
        MOVE_ORDER = 1

        max_index_list = []
        max_index = 0

        if MOVE_ORDER == 1:
            max_index = 4 * 3
        elif MOVE_ORDER == 2:
            max_index = 2 * 3

        for settlement_place, eval in evaluations.items():
            k = list(eval.keys())[max_index]
            max_index_list.append([settlement_place, k, eval[k]])

        max_index_list = sorted(max_index_list,key=lambda l:l[2])
        
        if MOVE_ORDER == 1:
            max_index_list = max_index_list[0:1]
        elif MOVE_ORDER == 2:
            max_index_list = max_index_list[0:4]
        elif MOVE_ORDER == 3:
            max_index_list = max_index_list[0:7]

        for m in max_index_list:
            print(m.index)
        print("")

        for settlement_place, eval in evaluations.items():
            print(f"{settlement_place.index}:")
            for i, v in eval.items():
                print(i.index, v)
            print("")

        while not won:
            steps += 1
            if draw:
                drawing.draw(board.hexagons, board.settlement_places, board.road_places, board.fish_pieces, board.buildable_road_places, board.robber)

            # actions = board.get_actions()
            # action = random.choice(tuple(actions))
            # board.move(action)
            # won = board.check_won()
    return steps / games, time.time() - s
  
if __name__ == '__main__':
    steps, t = play_games(games = 1, print_every = False, draw = True)
    print(f"average steps: {steps}")
    print(f"time: {t}")