import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import generator
from robber import Robber
from infrastructure import Settlement, Road, City
import random
from collections import defaultdict
from bank import Bank
import resources
import math
import board_loader
from encoder import encode, hexagons_to_string
import numpy as np

class Board:
    def __init__(self):
        self.bank = Bank()

        self.number = None
        self.players = generator.create_players()
        self.buildings = generator.create_start_buildings(self.players)

        self.player, self.building = self.buildings.pop(0)

        # number of half resources of players for robber
        self.resource_count_halved = {}
        self.temporary_player = None
        self.roads_built = 0
        self.resources_taken = 0

        self.temporary_actions = set()
            
        # self.settlement_places, self.road_places, self.hexagons = board_loader.load_board_save()
        
        self.settlement_places, self.road_places, self.hexagons, self.fish_pieces = generator.create_matrix()
        board_loader.save_board(self.settlement_places, self.road_places, self.hexagons)
        # import sys; sys.exit()

        generator.init_hexagons(self.hexagons, self.settlement_places)
        self.robber = Robber()

        self.buildable_settlement_places = defaultdict(set)
        self.unbuildable_settlement_places = set()
        self.buildable_road_places = defaultdict(set)
        self.buildable_city_places = {}
        
        self.victory_card_owners = dict.fromkeys(resources.victory_cards, None)

        # useful for hashing
        self.action_history = ""
        self.hexagons_str = hexagons_to_string(self.hexagons) 

    def __hash__(self):
        return hash(encode(self))

    def get_actions(self):
        if self.temporary_actions:
            return self.temporary_actions
        elif self.building:
            return self.player.get_actions_start(self, self.building)
        return self.player.get_actions(self)

    def check_won(self):
        for x in self.players:
            if x.get_victory_points() >= 10:
                return x

    def change_victory_card_owner(self, player, victory_card):
        owner = self.victory_card_owners[victory_card]

        if owner:
            owner.victory_cards.remove(victory_card)
            owner.add_victory_points(-2)

        player.victory_cards.append(victory_card)
        player.add_victory_points(2)
        self.victory_card_owners[victory_card] = player

    def build_settlement(self, player, settlement_place, allowed = None):

        settlement = Settlement(player, settlement_place)
        settlement_place.occupiedBy = settlement
        player.settlements.append(settlement)

        # increase players victory points
        player.add_victory_points(1)

        # allow three for one trading if player built at a 3:1 harbor
        harbor = settlement_place.harbor
        if harbor:
            if harbor.trade == "3:1":
                player.trade_three = True
            elif harbor.trade == "2:1":
                player.trade_two.add(harbor.resource)

        if not allowed:
            self.bank.pay_for_settlement(player)

        self.unbuildable_settlement_places.add(settlement_place.index)

        # remove from buildable settlement places
        self.buildable_settlement_places.pop(settlement_place.index, None)
        for settlement_neighbour in settlement_place.settlement_neighbours:
            self.unbuildable_settlement_places.add(settlement_neighbour.index)
            self.buildable_settlement_places.pop(settlement_neighbour.index, None)

        self.buildable_city_places[settlement_place.index] = player

        for neighbour in settlement_place.neighbours:
            if not neighbour.occupiedBy:
                self.buildable_road_places[neighbour.index].add(player)

    def build_road(self, player, road_place, allowed = None):

        road = Road(player, road_place)
        road_place.occupiedBy = road
        player.roads.append(road)

        if not allowed:
            self.bank.pay_for_road(player)

        del self.buildable_road_places[road_place.index]

        for neighbour in road_place.neighbours:
            if neighbour.index not in self.unbuildable_settlement_places:
                self.buildable_settlement_places[neighbour.index].add(player)

            if neighbour.occupiedBy is None or neighbour.occupiedBy.player == player:
                for road_neighbour in neighbour.neighbours:
                    if not road_neighbour.occupiedBy:
                        self.buildable_road_places[road_neighbour.index].add(player)

        if len(self.player.roads) >= 5:
            self.player.update_longest_road()

    def build_city(self, player, settlement_place):

        settlement = settlement_place.occupiedBy
        player.settlements.remove(settlement)
        city = City(player, settlement_place)
        settlement_place.occupiedBy = city
        player.cities.append(city)

        # increase players victory points
        player.add_victory_points(1)

        self.bank.pay_for_city(player)

        del self.buildable_city_places[settlement_place.index]

    def open_round(self):

        self.number = self.roll_dice()

        if self.number != 7:
            for x in self.players:
                x.take_resources(self.number, self.bank, self.robber)

    def get_building(self):
        # check if all starting buildings have been built
        if self.buildings:
            self.player, self.building = self.buildings.pop(0)
            return
        if self.building:
            self.building = None
            self.open_round()

    def move(self, action):
        self.action_history += str(action) + "."
        
        if action == 0:
            self.player = self.next_player()
            self.player.remove_play_protection()
            self.open_round()
        elif 2 <= action <= 55:
            self.build_settlement(self.player, self.settlement_places[action - 2], self.building)
        elif 56 <= action <= 127:
            self.build_road(self.player, self.road_places[action - 56], self.building)
            if self.roads_built:
                self.roads_built += 1
                if self.roads_built < 3:
                    self.temporary_actions = self.player.filter_road_places(self)
                else:
                    self.temporary_actions = set()
                    self.roads_built = 0
        elif 128 <= action <= 181:
            self.build_city(self.player, self.settlement_places[action - 128])
        elif 182 <= action <= 186:
            # trade four for one
            self.bank.pay(resources.resources[action - 182], 4, self.player)
            self.temporary_actions = set(range(197, 202))
        elif 187 <= action <= 191:
            # trade three for one
            self.bank.pay(resources.resources[action - 187], 3, self.player)
            self.temporary_actions = set(range(197, 202))
        elif 192 <= action <= 196:
            # trade two for one
            self.bank.pay(resources.resources[action - 192], 2, self.player)
            self.temporary_actions = set(range(197, 202))
        elif 197 <= action <= 201:
            # take resource
            self.bank.take(resources.resources[action - 197], 1, self.player)
            if self.resources_taken:
                self.resources_taken += 1
                if not self.resources_taken < 3:
                    self.temporary_actions = set()
                    self.resources_taken = 0
            else:
                self.temporary_actions = set()
        elif 202 <= action <= 206:
            # halve cards
            self.bank.pay(resources.resources[action - 202], 1, self.temporary_player)
            if sum(self.temporary_player.resources.values()) > self.resource_count_halved[self.temporary_player]:
                self.temporary_actions = self.temporary_player.p_pay()
            else:
                del self.resource_count_halved[self.temporary_player]
                if self.resource_count_halved:
                    self.temporary_player = next(iter(self.resource_count_halved))
                    self.temporary_actions = self.temporary_player.p_pay()
                else:
                    self.temporary_player = None
                    self.temporary_actions = self.player.p_robber(self)
        elif 207 <= action <= 225:
            hexagon = self.hexagons[action - 207]
            self.place_robber(hexagon)
            self.temporary_actions = self.player.p_draw_card_robber(hexagon, self.players)

        elif 226 <= action <= 228:
            self.player.draw_card(self.players[action - 226])
            self.temporary_actions = set()

        elif action == 229:
            dev_card = self.bank.get_dev_card(self.player)
            if dev_card.content == "siegpunkt":
                dev_card.played = True
                dev_card.play_protection = False
                self.player.add_victory_points(1)
            self.player.take_dev_card(dev_card)

        elif 230 <= action <= 234:
            self.player.use_dev_card("monopol")
            self.player.play_monopol(resources.resources[action - 230], self.players)

        elif action == 235:
            self.player.use_dev_card("ritter")
            self.temporary_actions = self.player.p_robber(self)

        elif action == 236:
            self.player.use_dev_card("straßenbau")
            self.roads_built += 1
            self.temporary_actions = self.player.filter_road_places(self)

        elif action == 237:
            self.player.use_dev_card("erfindung")
            self.resources_taken += 1
            self.temporary_actions = set(range(197, 202))

        elif action == 238:
            self.change_victory_card_owner(self.player, "rittermacht")

        elif action == 239:
            self.change_victory_card_owner(self.player, "längste handelsstraße")

        self.get_building()

    def place_robber(self, hexagon):
        self.robber.position = hexagon

    def roll_dice(self):
        dice1 = random.randrange(6) + 1
        dice2 = random.randrange(6) + 1
        return dice1 + dice2

    def next_player(self):
        index = self.players.index(self.player)
        if index + 1 == len(self.players):
            return self.players[0]
        return self.players[index + 1]

    def to_batch(self):

        conv_batch = []

        hexagon_numbers = np.zeros(shape = (23, 21), dtype=float)
        hexagon_resources = np.zeros(shape = (23, 21), dtype=float)
        for hexagon in self.hexagons:
            x, y = hexagon.matrix_pos
            hexagon_numbers[x][y] = hexagon.number
            hexagon_resources[x][y] = resources.all_resources.index(hexagon.resource)

        conv_batch.append(hexagon_numbers)
        conv_batch.append(hexagon_resources)

        for player in self.players:
            for l in player.settlements, player.roads, player.cities:
                buildings = np.zeros(shape = (23, 21), dtype=float)
                for building in l:
                    x, y = building.place.matrix_pos
                    buildings[x][y] = 1
                conv_batch.append(buildings)

        cur_player = np.zeros(shape = (23, 21), dtype=float) + (self.player.index - 1)
        conv_batch.append(cur_player)

        ff_batch = []

        for player in self.players:
            ff_batch.extend(player.resources.values())
            covered = 0
            for dev_cards in player.dev_cards.values():
                uncovered = 0
                for dev_card in dev_cards:
                    if dev_card.played:
                        uncovered += 1
                    else:
                        covered += 1
                ff_batch.append(uncovered)
            ff_batch.append(covered)
            for victory_card_owner in self.victory_card_owners.values():
                ff_batch.append((victory_card_owner == player) * 1)

        return conv_batch, ff_batch