import pygame
import os
import evaluation
from collections import defaultdict

BASEPATH = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

class Infrastructure_Place:
    def __init__(self, position, index, matrix_pos):
        self.bordersOn = []
        self.neighbours = []
        self.position = position
        self.index = index
        self.occupiedBy = None
        self.matrix_pos = matrix_pos
    def draw(self, screen, color = (0, 0, 0)):
        self.area = pygame.Rect(self.position[0] - 5, self.position[1] - 5, 10, 10)
        pygame.draw.rect(screen, color, self.area)
        if self.occupiedBy:
            self.occupiedBy.draw(screen)

class Settlement_Place(Infrastructure_Place):
    def __init__(self, position, index, matrix_pos, harbor = None, fish_piece = None):
        super().__init__(position, index, matrix_pos)
        self.harbor = harbor
        self.infrastructures_possible = [Settlement, City]
        self.settlement_neighbours = []
        self.fish_piece = fish_piece

    def __repr__(self):
        return str(self.index)

class Road_Place(Infrastructure_Place):
    def __init__(self, position, index, matrix_pos, rotation):
        super().__init__(position, index, matrix_pos)
        self.rotation = rotation
        self.road_neighbours = []
        self.infrastructures_possible = [Road]

    def __repr__(self):
        r = "Road_Place:\n"
        r += f"index: {self.index}\n"
        r += f"bordersOn: {self.bordersOn}\n"
        r += f"settlement neighbours: {len(self.neighbours)}\n"
        r += f"road neighbours: {len(self.road_neighbours)}\n"
        r += f"occupiedBy: {self.occupiedBy}\n"
        return r

class Harbor:
    def __init__(self, resource = None, trade = None):
        self.resource = resource
        self.trade = trade
    def __repr__(self):
        return f"{self.resource}, {self.trade}"

class Fish_Piece:
    def __init__(self, number, position, rotation):
        self.number = number
        self.position = position
        self.rotation = rotation

    def load_image(self):
        return pygame.image.load(f"{BASEPATH}/resources/fische/fisch{self.number}.png")

    def draw(self, screen):
        self.area = pygame.Rect(self.position[0] - 5, self.position[1] - 5, 10, 10)
        self.image = self.load_image()
        self.image = pygame.transform.rotate(self.image, self.rotation * 60)
        self.image_position = (self.position[0] - self.image.get_rect()[2] // 2, 
                               self.position[1] - self.image.get_rect()[3] // 2)

        screen.blit(self.image, self.image_position)

class Harbor_Piece:
    def __init__(self, harbors):
        self.harbors = harbors

class Infrastructure:
    def __init__(self, player, place):
        self.player = player
        self.place = place
    def draw(self, screen):
        position = self.place.position
        screen.blit(self.image, (position[0] - self.image.get_rect()[2] // 2, position[1] - self.image.get_rect()[3] // 2))
        self.image = None

class Road(Infrastructure):
    def __init__(self, player, place):
        super().__init__(player, place)
    def draw(self, screen):
        image = pygame.image.load(f"{BASEPATH}/resources/strassen/strasse_{self.player.color}.png")
        self.image = pygame.transform.rotate(image, self.place.rotation * 60)
        super().draw(screen)

class Settlement(Infrastructure):
    def __init__(self, player, place):
        super().__init__(player, place)
    def draw(self, screen):
        self.image = pygame.image.load(f"{BASEPATH}/resources/siedlungen/siedlung_{self.player.color}.png")
        super().draw(screen)

class City(Infrastructure):
    def __init__(self, player, place):
        super().__init__(player, place)
    def draw(self, screen):
        self.image = pygame.image.load(f"{BASEPATH}/resources/staedte/stadt_{self.player.color}.png")
        super().draw(screen)