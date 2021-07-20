from infrastructure import Road, Settlement, City, Road_Place, Settlement_Place
from node import Node
import numpy as np
import random
import resources
import itertools
from collections import defaultdict

class Player:
    def __init__(self, color, color_code, index):
        self.index = index
        self.color = color
        self.color_code = color_code
        self.settlements = []
        self.cities = []
        self.roads = []
        self.n_roads = 15
        self.n_settlements = 5
        self.n_cities = 4
        self.resources = dict.fromkeys(resources.resources, 0)
        self.dev_cards = {item: [] for item in resources.dev_cards}
        self.victory_cards = []
        self.dev_card_played_this_round = False
        self.longest_road_count = 0
        self.trade_three = False
        self.trade_two = set()
        self.victory_points = 0

    def __repr__(self):
        return f"P{self.index}"

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.index == other.index
        return False

    def __hash__(self):
        return hash(self.color)

    def get_victory_points(self):
        return self.victory_points

    def take_resources(self, number, bank, robber):
        for settlement in self.settlements:
            for hexagon in settlement.place.bordersOn:
                if hexagon.number == number and robber.position != hexagon:
                    bank.take(hexagon.resource, 1, self)
        for city in self.cities:
            for hexagon in city.place.bordersOn:
                if hexagon.number == number and robber.position != hexagon:
                    bank.take(hexagon.resource, 2, self)

    def add_victory_points(self, increment):
        self.victory_points += increment

    # longest road
    def update_longest_road(self):
        self.longest_road_count = 0
        roads_neighbours = {}

        for road in self.roads:
            neighbours = []
            for road_neighbour in road.place.road_neighbours:
                if road_neighbour.occupiedBy is not None and road_neighbour.occupiedBy.player == self:
                    neighbours.append(road_neighbour.occupiedBy)
            roads_neighbours[road] = neighbours

        for road in roads_neighbours:
            node = Node(None, roads_neighbours[road], 1, road)
            self.longest_road_helper(node, roads_neighbours)

    def longest_road_helper(self, previous_node, roads_neighbours):
        if previous_node.counter > self.longest_road_count: 
            self.longest_road_count = previous_node.counter

        for road in previous_node.neighbours:
            node = Node(previous_node, roads_neighbours[road], previous_node.counter + 1, road)
            node.delete_neighbours()
            self.longest_road_helper(node, roads_neighbours)

    def get_action_sample(self, board):
        actions = self.get_actions(board)
        return random.sample(actions, 1)[0]

    def p_build_settlement(self):
        return self.resources["holz"] > 0 and \
               self.resources["lehm"] > 0 and \
               self.resources["schaf"] > 0 and \
               self.resources["getreide"] > 0 and \
               len(self.settlements) < self.n_settlements

    def p_build_road(self):
        return self.resources["holz"] > 0 and \
               self.resources["lehm"] > 0 and \
               len(self.roads) < self.n_roads

    def p_build_city(self):
        return self.resources["stein"] >= 3 and \
               self.resources["getreide"] >= 2 and \
               len(self.cities) < self.n_cities

    def p_trade_four(self, offset = 182):
        return {i + offset for i, resource in enumerate(resources.resources) if self.resources[resource] >= 4}

    def p_trade_three(self, offset = 187):
        actions = set()
        if self.trade_three:
            actions = {i + offset for i, resource in enumerate(resources.resources) if self.resources[resource] >= 3}
        return actions

    def p_trade_two(self, offset = 192):
        actions = set()
        for resource in self.trade_two:
            if self.resources[resource] >= 2:
                actions.add(resources.resources.index(resource) + offset)
        return actions

    def p_pay(self, offset = 202):
        actions = set()
        for i, amount in enumerate(self.resources.values()):
            if amount > 0:
                actions.add(i + offset)
        return actions

    def p_robber(self, board, offset = 207):
        actions = set()
        for i, x in enumerate(board.hexagons):
            if x != board.robber.position:
                actions.add(i + offset)
        return actions

    def p_draw_card_robber(self, hexagon, players, offset = 226):
        actions = set()
        for x in hexagon.neighbours:
            if x.occupiedBy is not None:
                player = x.occupiedBy.player
                actions.add(players.index(player) + offset)
        return actions

    def p_play_dev(self, content):
        for x in self.dev_cards[content]:
            if not x.played and not x.play_protection:
                return True

    def p_take_knight_power(self, players):
        if not "rittermacht" in self.victory_cards:
            knights = len([x for x in self.dev_cards["ritter"] if x.played])
            if knights >= 3:
                owner = 0
                for x in [player for player in players if player != self]:
                    if "rittermacht" in x.victory_cards:
                        owner = len([x for x in self.dev_cards["ritter"] if x.played])
                return knights > owner

    def p_take_longest_road(self, players):
        if not "längste handelsstraße" in self.victory_cards:
            if self.longest_road_count >= 5:
                owner = 0
                for x in [player for player in players if player != self]:
                    if "längste handelsstraße" in x.victory_cards:
                        owner = self.longest_road_count
                return self.longest_road_count > owner       

    def draw_card(self, player):
        values = [i for i, x in enumerate(player.resources.values()) if x > 0]
        if values:
            random_index = random.choice(values)
            key = list(player.resources.keys())[random_index]
            player.resources[key] -= 1
            self.resources[key] += 1

    def use_dev_card(self, content):
        self.dev_card_played_this_round = True
        for x in self.dev_cards[content]:
            if not x.played:
               x.played = True
               break

    def remove_play_protection(self):
        self.dev_card_played_this_round = False
        for dev_cards in self.dev_cards.values():
            for dev_card in dev_cards:
                dev_card.play_protection = False

    def play_monopol(self, resource, players):
        for x in players:
            if x != self:
                amount = x.resources[resource]
                self.resources[resource] += amount
                x.resources[resource] -= amount

    def take_dev_card(self, dev_card):
        self.dev_cards[dev_card.content].append(dev_card)

    def get_actions_start(self, board, allowed):
        if allowed == Settlement:
            return self.get_settlement_places_start(board)
        elif allowed == Road:
            return self.get_road_places_start(board)

    # get the available settlement places at the beginning of the game
    def get_settlement_places_start(self, board, offset = 2):
        actions = set()
        for action in (set(range(54)) - board.unbuildable_settlement_places):
            actions.add(action + offset)
        return actions

    # get the available road places at the beginning of the game
    def get_road_places_start(self, board, offset = 56):
        actions = set()
        for action, players in board.buildable_road_places.items():
            if self in players:
                if action not in [neighbour.index for neighbour in self.settlements[-1].place.neighbours]:
                    continue
                actions.add(action + offset)
        return actions

    def filter_settlement_places(self, board, offset = 2):
        return {action + offset for action, players in board.buildable_settlement_places.items() if self in players}

    def filter_road_places(self, board, offset = 56):
        return {action + offset for action, players in board.buildable_road_places.items() if self in players}

    def filter_city_places(self, board, offset = 128):
        return {action + offset for action, player in board.buildable_city_places.items() if self == player}

    def p_pre_round(self):
        actions = set()
        actions.add(1)
        if self.p_play_dev("ritter"):
            actions.add(235)
        return actions

    def get_actions(self, board):

        actions = set()

        # action to finish the players turn
        actions.add(0)

        if self.p_build_settlement():
            actions.update(self.filter_settlement_places(board))

        if self.p_build_road():
            actions.update(self.filter_road_places(board))

        if self.p_build_city():
            actions.update(self.filter_city_places(board))

        actions.update(self.p_trade_four())
        actions.update(self.p_trade_three())
        actions.update(self.p_trade_two())

        if self.p_take_knight_power(board.players):
            actions.add(238)

        if self.p_take_longest_road(board.players):
            actions.add(239)

        return actions