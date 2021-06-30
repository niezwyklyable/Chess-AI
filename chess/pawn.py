
import pygame
from .constants import SQUARE_SIZE, PAWN_BLACK, PAWN_WHITE, FACTOR

class Pawn:

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.x = 0
        self.y = 0
        self.type = 'pawn'
        self.first_move = True
        self.calc_pos()
        self.move_counter = 0
        self.dx = 0
        self.dy = 0
        self.dir_x = 0
        self.dir_y = 0
        self.checking = False

    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def draw(self, win):
        if self.color == 'black':
            win.blit(PAWN_BLACK, (self.x - PAWN_BLACK.get_width() // 2, self.y - PAWN_BLACK.get_height() // 2))
        elif self.color == 'white':
            win.blit(PAWN_WHITE, (self.x - PAWN_WHITE.get_width() // 2, self.y - PAWN_WHITE.get_height() // 2))

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()
        self.first_move = False
        self.move_counter += 1

    def calc_dir(self, row, col):
        self.dir_x = SQUARE_SIZE * col + SQUARE_SIZE // 2
        self.dir_y = SQUARE_SIZE * row + SQUARE_SIZE // 2
        self.dx = (self.dir_x - self.x) / FACTOR
        self.dy = (self.dir_y - self.y) / FACTOR
