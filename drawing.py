import os
from hexagon import Hexagon
import itertools
import numpy as np
import resources
import pygame

def draw(board, resource_history = []):

    pygame.init()
    pygame.font.init()

    BASEPATH = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))        
    size = (1500, 900)
    screen = pygame.display.set_mode(size)
    screen.fill((255, 255, 255))
    board_image = pygame.image.load(f"{BASEPATH}/resources/spielbrett.jpg")
    center = board_image.get_rect().center
    new_rect = board_image.get_rect(center = center)

    screen.blit(board_image, new_rect)

    for hexagon in board.hexagons:
        hexagon.draw(screen, board.robber)
    for settlement_place in board.settlement_places:
        settlement_place.draw(screen)
    for road_place in board.road_places:
        color = (0, 0, 0)
        if road_place.index in board.buildable_road_places:
            players = board.buildable_road_places[road_place.index]
            if len(players) > 1:
                color = (73, 61, 79)
            else:
                color = list(players)[0].color_code
        road_place.draw(screen, color)
    for fish_piece in board.fish_pieces:
        fish_piece.draw(screen)

    pygame.draw.rect(screen, (0, 255, 255), (1030, 0, 500, 100))
    pygame.draw.rect(screen, (0, 255, 255), (1030, 100, 500, 100))
    pygame.draw.rect(screen, (0, 255, 255), (1030, 200, 500, 100))
    pygame.draw.rect(screen, (0, 255, 255), (1030, 400, 500, 300))

    myfont = pygame.font.SysFont('Arial', 15)

    for i, player in enumerate(board.players):
        textsurface = myfont.render(f"{player.resources}, {player.get_victory_points()}", False, (0, 0, 0))
        screen.blit(textsurface, (1100, i * 20 + 10))
        pygame.draw.rect(screen, player.color_code, (1080, i * 20 + 13, 10, 10))
        pygame.draw.rect(screen, player.color_code, (1080, i * 20 + 113, 10, 10))

    for i, player in enumerate(board.players):
        a = []
        for dev_cards in player.dev_cards.values():
            for dev_card in dev_cards:
                a.append(dev_card)
        textsurface = myfont.render(f"{a}", False, (0, 0, 0))
        screen.blit(textsurface, (1100, i * 20 + 210))
        pygame.draw.rect(screen, player.color_code, (1080, i * 20 + 213, 10, 10))

    resource_differences = []

    if len(resource_history) == 2:
        for i, _ in enumerate(resource_history[0]):
            resource_differences.append(list(np.array(resource_history[1][i]) - np.array(resource_history[0][i])))

    for i, resources_ in enumerate(resource_differences):
        textsurface = myfont.render(f"{dict(zip(resources.resources, resources_))}", False, (0, 0, 0))
        screen.blit(textsurface, (1100, i * 20 + 110))
    
    myfont = pygame.font.SysFont('Arial', 80)
    textsurface1 = myfont.render(f"{board.number}", False, (0, 0, 0))
    pygame.draw.rect(screen, board.player.color_code, (1150, 500, 100, 100))
    screen.blit(textsurface1, (1200, 400))


    myfont = pygame.font.SysFont('Arial', 12)
    pygame.draw.rect(screen, (255, 255, 255), (1000, 700, 400, 100))

    textsurface1 = myfont.render(f"", False, (0, 0, 0))

    pos = pygame.mouse.get_pos()
    
    for settlement_place in board.settlement_places:
        if settlement_place.area.collidepoint(pos):
            textsurface1 = myfont.render(f"{settlement_place}", False, (0, 0, 0))

    screen.blit(textsurface1, (1000, 750))

    pygame.display.update()