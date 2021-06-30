
import pygame

WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
FACTOR = 100
DELAY = 0

WHITE = (255, 255, 255)
GREY = (115, 103, 113)
BLUE = (0, 0, 255)
PINK = (209, 102, 188)
GREEN = (130, 232, 154)

PAWN_BLACK = pygame.transform.scale(pygame.image.load('images/pionCZ.png'), (100, 100))
PAWN_WHITE = pygame.transform.scale(pygame.image.load('images/pionB.png'), (100, 100))
ROOK_BLACK = pygame.transform.scale(pygame.image.load('images/wiezaCZ.png'), (100, 100))
ROOK_WHITE = pygame.transform.scale(pygame.image.load('images/wiezaB.png'), (100, 100))
KNIGHT_BLACK = pygame.transform.scale(pygame.image.load('images/konCZ.png'), (100, 100))
KNIGHT_WHITE = pygame.transform.scale(pygame.image.load('images/konB.png'), (100, 100))
BISHOP_BLACK = pygame.transform.scale(pygame.image.load('images/goniecCZ.png'), (100, 100))
BISHOP_WHITE = pygame.transform.scale(pygame.image.load('images/goniecB.png'), (100, 100))
QUEEN_BLACK = pygame.transform.scale(pygame.image.load('images/hetmanCZ.png'), (100, 100))
QUEEN_WHITE = pygame.transform.scale(pygame.image.load('images/hetmanB.png'), (100, 100))
KING_BLACK = pygame.transform.scale(pygame.image.load('images/krolCZ.png'), (100, 100))
KING_WHITE = pygame.transform.scale(pygame.image.load('images/krolB.png'), (100, 100))
