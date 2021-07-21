import os
from hexagon import Hexagon
import itertools
import numpy as np
import resources
import pygame

def draw(hexagons, settlement_places, road_places, fish_pieces, buildable_road_places = None, robber = None):

    pygame.init()
    pygame.font.init()

    BASEPATH = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))        
    size = (1000, 865)
    screen = pygame.display.set_mode(size)
    screen.fill((255, 255, 255))
    board_image = pygame.image.load(f"{BASEPATH}/resources/spielbrett.jpg")
    center = board_image.get_rect().center
    new_rect = board_image.get_rect(center = center)

    screen.blit(board_image, new_rect)

    for hexagon in hexagons:
        hexagon.draw(screen, robber)
    for settlement_place in settlement_places:
        settlement_place.draw(screen)
    for road_place in road_places:
        if buildable_road_places:
            color = (0, 0, 0)
            if road_place.index in buildable_road_places:
                players = buildable_road_places[road_place.index]
                if len(players) > 1:
                    color = (73, 61, 79)
                else:
                    color = list(players)[0].color_code
            road_place.draw(screen, color)
    for fish_piece in fish_pieces:
        fish_piece.draw(screen)

    myfont = pygame.font.SysFont('Arial', 15)

    pos = pygame.mouse.get_pos()
    
    textsurface1 = None

    for settlement_place in settlement_places:
        if settlement_place.area.collidepoint(pos):
            textsurface1 = myfont.render(f"{settlement_place}", False, (0, 0, 0))
            screen.blit(textsurface1, (10, 10))

    pygame.display.update()


# def draw_(hexagons, settlement_places, road_places, fish_pieces):

#     pygame.init()
#     pygame.font.init()

#     BASEPATH = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))        
#     size = (1000, 865)
#     screen = pygame.display.set_mode(size)
#     screen.fill((255, 255, 255))
#     board_image = pygame.image.load(f"{BASEPATH}/resources/spielbrett.jpg")
#     center = board_image.get_rect().center
#     new_rect = board_image.get_rect(center = center)

#     screen.blit(board_image, new_rect)

#     for hexagon in hexagons:
#         hexagon.draw(screen)
#     for settlement_place in settlement_places:
#         settlement_place.draw(screen)
#     for fish_piece in fish_pieces:
#         fish_piece.draw(screen)

#     pygame.display.update()