import copy
from encoder import hexagons_to_string
from random import shuffle
from infrastructure import Fish_Piece, Road_Place, Settlement_Place, Harbor, Harbor_Piece, Road, Settlement
import numpy as np
import os
from hexagon import Hexagon
from player import Player
import random
from bank import Bank
import math
from evaluation import probability
import drawing

RESOURCES = ['getreide', 'getreide', 'getreide', 'getreide', 'holz', 'holz', 'holz', 'holz', 'lehm', 'lehm', 'lehm', 'schaf', 'schaf', 'schaf', 'schaf', 'stein', 'stein', 'stein']
NUMBERS = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]

def get_number(n, target, numbers):
    total_prob = sum([probability(x) for x in n])                                   # calculate value of current place
    probabilities = [probability(x) + total_prob for x in numbers]                  # add value of numbers to current place
    deltas = [abs(prob - target) for prob in probabilities]                         # see which number's probability is closest to target
    deltas = [math.inf if numbers[i] in n else d for (i, d) in enumerate(deltas)]   # filter same numbers
    return numbers[deltas.index(min(deltas))] 

def create_resource_distribution(n_resources, numbers):
    numbers_taken = []
    for i in range(n_resources):
        x = get_number(numbers_taken, (0.3222 + random.uniform(-0.1, 0.1)) * (i + 1)/4, numbers)
        numbers.remove(x)
        numbers_taken.append(x)
    return numbers_taken

def distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def resource_in_hexagons(resource, hexagons):
    for hexagon in hexagons:
        if hexagon.resource and hexagon.resource == resource:
            return True
    return False

def red_number_in_hexagons(hexagons):
    for hexagon in hexagons:
        if hexagon.number in [6, 8]:
            return True
    return False

def different_resource(resource_number_distribution_t, neighbours):
    for x in resource_number_distribution_t:
        if not resource_in_hexagons(x[0], neighbours):
            if not (x[1] in [6, 8] and red_number_in_hexagons(neighbours)):
                return x
    return resource_number_distribution_t[0]

def init_hexagons(hexagons, settlement_places, road_places, fish_pieces):

    resources = copy.deepcopy(RESOURCES)
    shuffle(resources)

    possible_lake_indexes = [4, 5, 8, 10, 13, 14]
    lake_index = random.choice(possible_lake_indexes)

    for hexagon in hexagons:
        if hexagon.index == lake_index:
            hexagon.resource = "fisch"
            hexagon.number = [2, 3, 11, 12]

    # hexagon initialization start

    numbers = copy.deepcopy(NUMBERS)
    shuffle(numbers)

    resource_number_distribution = {'getreide': create_resource_distribution(4, numbers),
                                    'schaf': create_resource_distribution(4, numbers),
                                    'holz': create_resource_distribution(4, numbers),
                                    'lehm': create_resource_distribution(3, numbers),
                                    'stein': create_resource_distribution(3, numbers)}

    print(resource_number_distribution)

    resource_number_distribution_t = []
    for resource, n in resource_number_distribution.items():
        for x in n:
            resource_number_distribution_t.append((resource, x))

    shuffle(resource_number_distribution_t)

    for hexagon in hexagons:
        if hexagon.resource is None:
            neighbours = hexagon.hexagon_neighbours

            x = different_resource(resource_number_distribution_t, neighbours)
            hexagon.resource = x[0]
            hexagon.number = x[1]
            resource_number_distribution_t.remove(x)

            drawing.draw(hexagons, settlement_places, road_places, fish_pieces)

    # hexagon initialization end

def init_hexagons_save(hexagons, resources, numbers):
    for hexagon in hexagons:
        hexagon.resource = resources.pop(0)
        hexagon.number = numbers.pop(0)

def make_graph():

    matrix_width = 21
    matrix_height = 23

    matrix = np.zeros(shape = (matrix_height, matrix_width), dtype=object)

    # settlements

    settlement_places = []

    n = 3
    start = 6
    step = 1
    counter = 0
    height = 85
    settlement_index = 0

    for i in range(12):
        for x in range(start, start + n * (4), 4):
            harbor = None
            if x + 4 >= start + n * 4 or x == start or counter in [0, 2, 20, 22]: harbor = Harbor()

            position = (x * 38 + 120, height)

            settlement_place = Settlement_Place(position, settlement_index, (counter, x), harbor)

            matrix[counter][x] = settlement_place
            settlement_index += 1
            settlement_places.append(settlement_place)
                
        if (counter + 2) % 4 == 0: 
            height += 90
        else:
            height += 40

        counter += 2
        step = (i + 1) % 2
        if i > 5: step = -step
        n += step
        start -= step * 2

    # roads

    road_places = []
    hexagons = []

    n = 6
    start = 5
    step = 1
    counter = 1
    added = 0
    height = 105
    rotation_counter = 0
    hexagon_counter = 0
    road_index = 0

    for i in range(11):
        for x in range(start, start + n * (2), 2):
            position = (x * 38 + 120, height)
            if (counter + 1) % 4 == 0:
                if (added + 1) % 2 == 0:
                    # resource = None
                    # number = None
                    # if hexagon_counter == 9:
                    #     number = 7
                    #     resource = "wueste"

                    hexagon = Hexagon(position, hexagon_counter, (counter, x))

                    matrix[counter][x] = hexagon
                    hexagon_counter += 1
                    hexagons.append(hexagon)
                else:
                    road_place = Road_Place(position, road_index, (counter, x), 0)

                    matrix[counter][x] = road_place
                    road_index += 1
                    road_places.append(road_place)
                added += 1
            else:
                if rotation_counter % 2 == 0:

                    road_place = Road_Place(position, road_index, (counter, x), -1)

                    matrix[counter][x] = road_place
                    road_index += 1
                    road_places.append(road_place)
                else:
                    road_place = Road_Place(position, road_index, (counter, x), 1)

                    matrix[counter][x] = road_place
                    road_index += 1
                    road_places.append(road_place)
                rotation_counter += 1
        
        rotation_counter = 0
        height += 65

        added = 0
        counter += 2
        if i == 5: 
            step = -step
        if i >= 5:
            rotation_counter = 1
        n += step
        start += -step

    return matrix, settlement_places, road_places, hexagons

def index_exists(r, c, matrix):
    return 0 <= r < len(matrix) and 0 <= c < len(matrix[0])

def append_neighbour(r, s):
    if type(r) == Road_Place:
        s.neighbours.append(r)
        r.neighbours.append(s)

def make_hexagon_neighbours(index, deltaY, deltaX, matrix, hexagon):
    index_valid = index_exists(index[0] + deltaY, index[1] + deltaX, matrix)
    if index_valid:
        neighbour = matrix[index[0] + deltaY][index[1] + deltaX]
        if type(neighbour) == Hexagon:
            if neighbour not in hexagon.hexagon_neighbours:
                hexagon.hexagon_neighbours.append(neighbour)
            if hexagon not in neighbour.hexagon_neighbours:
                neighbour.hexagon_neighbours.append(hexagon)

def make_neighbours(index, deltaY, deltaX, matrix, element, hexagon = False, settlement = False, road = False):
    index_valid = index_exists(index[0] + deltaY, index[1] + deltaX, matrix)
    if index_valid:
        neighbour = matrix[index[0] + deltaY][index[1] + deltaX]
        if hexagon:
            if type(neighbour) == Hexagon:
                element.bordersOn.append(neighbour)
                neighbour.neighbours.append(element)
        elif settlement:
            if type(neighbour) == Settlement_Place:
                element.settlement_neighbours.append(neighbour)
        elif road:
            if type(neighbour) == Road_Place:
                element.road_neighbours.append(neighbour)
        else:
            append_neighbour(neighbour, element)

def neighbours(matrix, settlement_places, road_places, hexagons):

    for element in settlement_places:
        index = np.where(matrix == element)
        index = [index[0][0], index[1][0]]

        # roads
        make_neighbours(index, 1, -1, matrix, element)
        make_neighbours(index, 1, 1, matrix, element)
        make_neighbours(index, -1, -1, matrix, element)
        make_neighbours(index, -1, 1, matrix, element)
        make_neighbours(index, -1, 0, matrix, element)
        make_neighbours(index, 1, 0, matrix, element)

        # hexagons
        make_neighbours(index, 3, 0, matrix, element, True)
        make_neighbours(index, -3, 0, matrix, element, True)
        make_neighbours(index, 1, -2, matrix, element, True)
        make_neighbours(index, -1, -2, matrix, element, True)
        make_neighbours(index, 1, 2, matrix, element, True)
        make_neighbours(index, -1, 2, matrix, element, True)

        # settlements
        make_neighbours(index, -2, 2, matrix, element, False, True)
        make_neighbours(index, -2, -2, matrix, element, False, True)
        make_neighbours(index, 2, 0, matrix, element, False, True)
        make_neighbours(index, -2, 0, matrix, element, False, True)
        make_neighbours(index, 2, 2, matrix, element, False, True)
        make_neighbours(index, 2, -2, matrix, element, False, True)

    for element in road_places:
        index = np.where(matrix == element)
        index = [index[0][0], index[1][0]]

        # road neighbours
        make_neighbours(index, -2, -1, matrix, element, False, False, True)
        make_neighbours(index, -2, 1, matrix, element, False, False, True)
        make_neighbours(index, 2, -1, matrix, element, False, False, True)
        make_neighbours(index, 2, 1, matrix, element, False, False, True)
        make_neighbours(index, 0, 2, matrix, element, False, False, True)
        make_neighbours(index, 0, -2, matrix, element, False, False, True)

    for element in hexagons:
        index = np.where(matrix == element)
        index = [index[0][0], index[1][0]]

        # hexagon neighbours
        make_hexagon_neighbours(index, -4, -2, matrix, element)
        make_hexagon_neighbours(index, -4, 2, matrix, element)
        make_hexagon_neighbours(index, 4, -2, matrix, element)
        make_hexagon_neighbours(index, 4, 2, matrix, element)
        make_hexagon_neighbours(index, 0, -4, matrix, element)
        make_hexagon_neighbours(index, 0, 4, matrix, element)

def make_harbor(settlement, previous, start, harbors, counter, fish_pieces_indexes, fish_pieces):

    harbor = harbors.pop()
    settlement.harbor = harbor

    if fish_pieces_indexes and counter in fish_pieces_indexes:
        settlement.fish_piece = fish_pieces[math.floor((fish_pieces_indexes.index(counter)) / 3)]

    for road in settlement.neighbours:
        for neighbour in road.neighbours:
            if neighbour.harbor is not None:
                if neighbour not in [settlement, start, previous]:
                    make_harbor(neighbour, settlement, start, harbors, counter + 1, fish_pieces_indexes, fish_pieces)

def make_harbors(matrix):
    start = matrix[2][4]
    settlement = matrix[0][6]

    harbors = [Harbor_Piece([Harbor(), Harbor(), Harbor("stein", "2:1"), Harbor("stein", "2:1"), Harbor()]),
               Harbor_Piece([Harbor("alle", "3:1"), Harbor("alle", "3:1"), Harbor(), Harbor("schaf", "2:1"), Harbor("schaf", "2:1")]),
               Harbor_Piece([Harbor(), Harbor(), Harbor("alle", "3:1"), Harbor("alle", "3:1"), Harbor()]),
               Harbor_Piece([Harbor("alle", "3:1"), Harbor("alle", "3:1"), Harbor(), Harbor("lehm", "2:1"), Harbor("lehm", "2:1")]),
               Harbor_Piece([Harbor(), Harbor(), Harbor("holz", "2:1"), Harbor("holz", "2:1"), Harbor()]),
               Harbor_Piece([Harbor("alle", "3:1"), Harbor("alle", "3:1"), Harbor(), Harbor("getreide", "2:1"), Harbor("getreide", "2:1")])]

    harbor_list = []
    for harbor_piece in harbors:
        for harbor in harbor_piece.harbors:
            harbor_list.append(harbor)

    harbor_list = list(reversed(harbor_list))

    counter = 1

    # fish pieces

    fish_pieces_indexes = [4, 5, 6, 7, 8, 9, 14, 15, 16, 17, 18, 19, 24, 25, 26, 27, 28, 29]

    fish_pieces = []
    fish_pieces_numbers = [4, 5, 6, 8, 9, 10]
    shuffle(fish_pieces_numbers)
    fish_pieces_positions = [[(575, 70), 0], [(775, 185), -1], [(775, 675), -2], [(575, 790), -3], [(145, 545), 2], [(145, 315), 1]]

    for fish_pieces_number, fish_pieces_position in zip(fish_pieces_numbers, fish_pieces_positions):
        fish_pieces.append(Fish_Piece(fish_pieces_number, fish_pieces_position[0], fish_pieces_position[1]))

    harbor = harbor_list.pop()
    start.harbor = harbor

    counter += 1

    make_harbor(settlement, start, start, harbor_list, counter, fish_pieces_indexes, fish_pieces)

    return fish_pieces

def create_matrix():
    matrix, settlement_places, road_places, hexagons = make_graph()
    neighbours(matrix, settlement_places, road_places, hexagons)
    fish_pieces = make_harbors(matrix)
    return settlement_places, road_places, hexagons, fish_pieces

def rotate(l, n):
    return l[-n:] + l[:-n]

def create_players(rotation = None):
    players = [Player('weiss', (255, 255, 255), 1),
               Player('orange', (255, 165, 0), 2)]
               # Player('blau', (18, 39, 158))#
    if rotation is None:
        rotation = random.randrange(len(players))
    return rotate(players, rotation)

def create_start_buildings(players):
    buildings = []
    for player in players:
        buildings.append((player, Settlement))
        buildings.append((player, Road))
    for player in reversed(players):
        buildings.append((player, Settlement))
        buildings.append((player, Road))
    return buildings