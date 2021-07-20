import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from board import Board
import random
import drawing
import copy
import board_loader
from cards import DevCard

def print_stats(board):
    for player in board.players:
        print(f"player {player.index}")
        print(f"settlements: {len(player.settlements)}")
        print(f"roads: {len(player.roads)}")
        print(f"cities: {len(player.cities)}")
        print(f"resources: {player.resources}")
        print(f"dev cards: {player.dev_cards}")
        print(f"victory cards: {player.victory_cards}")
        print(f"longest road count: {player.longest_road_count}")
        print(f"trade three available: {player.trade_three}")
        print(f"trade two available: {player.trade_two}")
        print(f"victory points: {player.victory_points}")
        print("")

def play_games(games = 1):
    counter = 0
    for _ in range(games):
        won = False
        board = Board()
        board.player.dev_cards["erfindung"].append(DevCard("erfindung"))
        while not won:
            counter += 1
            drawing.draw(board)
            actions = board.get_actions()
            if actions == set([1]):
                action = 1
            else:
                print(f"counter: {counter}")
                print(actions)
                action = -1
                while action not in actions:
                    try:
                        action = int(input("Aktion: "))
                    except ValueError:
                        print("Not a number. Try again:")
                        action = -1
            board.move(action)
            won = board.check_won()
        
        print_stats(board)
  
play_games(1)