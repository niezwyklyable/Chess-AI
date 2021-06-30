
import pygame
from chess.constants import WIDTH, HEIGHT, SQUARE_SIZE
from chess.board import Board
from chess.minimax import minimax

FPS = 60

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Chess AI v2.1 by AW')

def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def main():
    run = True
    clock = pygame.time.Clock()
    board = Board(WIN)
    
    while run:
        clock.tick(FPS)

        # AI bez roszady i bez bicia w przelocie
        if board.turn == 'black' and not board.gameover:
            temp_dict = {'white_pawns': 0,
                        'black_pawns': 0,
                        'white_rooks': 0,
                        'black_rooks': 0,
                        'white_knights': 0,
                        'black_knights': 0,
                        'white_bishops': 0,
                        'black_bishops': 0,
                        'white_queens': 0,
                        'black_queens': 0,
                        'white_king': 0,
                        'black_king': 0,
                        'white_checkmate_reward': 0,
                        'black_checkmate_reward': 0,
                        'checking_figure_is_beaten': False,
                        'gameover': False}
            _, figure, new_row, new_col = minimax(board.board, 2, True, board, temp_dict)
            #print('figure.row:', figure.row)
            #print('figure.col:', figure.col)
            #print('new_row:', new_row)
            #print('new_col:', new_col)
            board.select(figure.row, figure.col)
            board.select(new_row, new_col)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                LMB, _, RMB = pygame.mouse.get_pressed(3)
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                if not board.gameover:
                    if LMB:
                        board.select(row, col)
                    elif RMB:
                        board.castling(board.board, row, col)

        board.update()

    pygame.quit()

main()
