import pygame
import os

BASEPATH = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

pygame.font.init()
myfont = pygame.font.SysFont('Arial', 15)

class Hexagon:
    def __init__(self, position, index, matrix_pos):
        self.position = position
        self.resource = None
        self.number = None
        self.index = index
        self.neighbours = []
        self.matrix_pos = matrix_pos

    def __repr__(self):
        return f"Hexagon: ({self.number}, {self.resource})"

    def load_image(self):
        return pygame.image.load(f"{BASEPATH}/resources/hexagone/hex_{self.resource}.png")

    def draw(self, screen, robber):
        self.area = pygame.Rect(self.position[0] - 15, self.position[1] - 15, 30, 30)
        self.image = self.load_image()
        self.image_position = (self.position[0] - self.image.get_rect()[2] // 2, 
                               self.position[1] - self.image.get_rect()[3] // 2)

        screen.blit(self.image, self.image_position)
        
        if not type(self.number) == list:
            self.draw_circle(screen, robber)
            self.draw_number(screen, robber)

        self.image = None
        self.image_position = None

    def draw_circle(self, screen, robber):
        color = (255, 255, 255)
        if robber.position == self: color = (0, 0, 0)
        self.circle_radius = 13
        self.circle_x = self.image_position[0] + int(self.image.get_rect()[2]/2)
        self.circle_y = self.image_position[1] + int(self.image.get_rect()[3]/2)
        pygame.draw.circle(screen, color, (self.circle_x, self.circle_y), self.circle_radius)

    def draw_number(self, screen, robber):
        color = (0, 0, 0)
        if robber.position == self: color = (255, 255, 255)
        textsurface = myfont.render(str(self.number), False, color)
        screen.blit(textsurface, (self.circle_x - 3 - (self.number > 9) * 4, self.circle_y - 9))