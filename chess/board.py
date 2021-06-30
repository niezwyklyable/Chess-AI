
import pygame
from copy import deepcopy

from .constants import WHITE, GREY, SQUARE_SIZE, ROWS, COLS, BLUE, PINK, GREEN, DELAY
from .pawn import Pawn
from .rook import Rook
from .knight import Knight
from .bishop import Bishop
from .queen import Queen
from .king import King

class Board:
    def __init__(self, WIN):
        self.board = []
        self.create_board()
        self.valid_moves = []
        self.turn = 'white'
        self.selected = None
        self.selected_king_for_castling = None
        self.selected_rook_for_castling = None
        self.gameover = False
        self.beating_in_flight = False
        self.beating_in_flight_can_be_set = True
        self.last_move = None
        self.win = WIN

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if row == 0:
                    if col == 0 or col == 7:
                        self.board[row].append(Rook(row, col, 'white'))
                    elif col == 1 or col == 6:
                        self.board[row].append(Knight(row, col, 'white'))
                    elif col == 2 or col == 5:
                        self.board[row].append(Bishop(row, col, 'white'))
                    elif col == 3:
                        self.board[row].append(Queen(row, col, 'white'))
                    elif col == 4:
                        self.board[row].append(King(row, col, 'white'))
                elif row == 1:
                    self.board[row].append(Pawn(row, col, 'white'))
                elif row == 6:
                    self.board[row].append(Pawn(row, col, 'black'))
                elif row == 7:
                    if col == 0 or col == 7:
                        self.board[row].append(Rook(row, col, 'black'))
                    elif col == 1 or col == 6:
                        self.board[row].append(Knight(row, col, 'black'))
                    elif col == 2 or col == 5:
                        self.board[row].append(Bishop(row, col, 'black'))
                    elif col == 3:
                        self.board[row].append(Queen(row, col, 'black'))
                    elif col == 4:
                        self.board[row].append(King(row, col, 'black'))
                else:
                    self.board[row].append(0)

    def draw_squares(self):
        self.win.fill(WHITE)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(self.win, GREY, (row*SQUARE_SIZE, col*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_figures(self):
        for row in range(ROWS):
            for col in range(COLS):
                figure = self.board[row][col]
                if figure != 0:
                    figure.draw(self.win)

    def draw_selected(self):
        if self.selected:
            if self.selected.color == self.turn:
                pygame.draw.rect(self.win, PINK, (self.selected.col*SQUARE_SIZE, self.selected.row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        if self.selected_king_for_castling:
            pygame.draw.rect(self.win, PINK, (self.selected_king_for_castling.col*SQUARE_SIZE, self.selected_king_for_castling.row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        if self.selected_rook_for_castling:
            pygame.draw.rect(self.win, PINK, (self.selected_rook_for_castling.col*SQUARE_SIZE, self.selected_rook_for_castling.row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_valid_moves(self, moves):
        if self.selected:
            for move in moves:
                row, col = move
                pygame.draw.circle(self.win, BLUE, (col*SQUARE_SIZE + SQUARE_SIZE // 2, row*SQUARE_SIZE + SQUARE_SIZE // 2), 15)
        
        if self.selected_king_for_castling or self.selected_rook_for_castling:
            for move in moves:
                row, col = move
                pygame.draw.circle(self.win, GREEN, (col*SQUARE_SIZE + SQUARE_SIZE // 2, row*SQUARE_SIZE + SQUARE_SIZE // 2), 15)

    def update(self):
        self.draw_squares()
        self.draw_selected()
        self.draw_figures()
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def visualization(self, figure):
        figure.x += figure.dx
        figure.y += figure.dy
        #pygame.time.delay(DELAY)
        self.update()
        if figure.x == figure.dir_x and figure.y == figure.dir_y:
            return
        else:
            self.visualization(figure)

    def select(self, row, col):
        self.selected_king_for_castling = None
        self.selected_rook_for_castling = None
        if self.selected:
            if self.selected.color == self.turn:
                if (row, col) in self.valid_moves:
                    self.beating_in_flight_can_be_set = False # flaga ta zabezpiecza flage beating_in_flight przed niepozadanym zapaleniem - uniemozliwia metodzie get_valid_moves_for_pawns ustawienie flagi beating_in_flight na wirtualnych szachownicach
                    if self.verify_invalid_moves(deepcopy(self.board), deepcopy(self.selected), row, col):
                        if self.selected.color == 'white':
                            print('Black player: Cannot move! It would be a check!')
                        else:
                            print('White player: Cannot move! It would be a check!')
                        self.beating_in_flight_can_be_set = True
                        self.beating_in_flight = False
                        return
                    if self.beating_in_flight:
                        # usuniecie zbijanej figury podczas bicia w przelocie
                        self.board[self.selected.row][col] = 0
                    self.move(self.selected, row, col)
                    self.beating_in_flight_can_be_set = True
                    self.beating_in_flight = False
                    return

        self.selected = self.board[row][col]
        if self.selected != 0 and self.selected.color == self.turn:
            self.beating_in_flight = False
            if self.selected.type == 'pawn':
                self.valid_moves = self.get_valid_moves_for_pawns(self.board, self.selected)
            elif self.selected.type == 'rook':
                self.valid_moves = self.get_valid_moves_for_rooks(self.board, self.selected)
            elif self.selected.type == 'knight':
                self.valid_moves = self.get_valid_moves_for_knights(self.board, self.selected)
            elif self.selected.type == 'bishop':
                self.valid_moves = self.get_valid_moves_for_bishops(self.board, self.selected)
            elif self.selected.type == 'queen':
                self.valid_moves = self.get_valid_moves_for_bishops(self.board, self.selected) + self.get_valid_moves_for_rooks(self.board, self.selected)
            elif self.selected.type == 'king':
                self.valid_moves = self.get_valid_moves_for_kings(self.board, self.selected)

    def move(self, figure, row, col):
        self.board[figure.row][figure.col], self.board[row][col] = 0, self.board[figure.row][figure.col]
        figure.calc_dir(row, col)
        self.visualization(figure)
        figure.move(row, col)
        self.last_move = figure
        # promocja piona
        if figure.type == 'pawn' and figure.color == 'white' and figure.row == 7:
            self.board[row][col] = Queen(row, col, 'white')
        if figure.type == 'pawn' and figure.color == 'black' and figure.row == 0:
            self.board[row][col] = Queen(row, col, 'black')
        # zaszachowanie przez figure ktora wlasnie dokonala ruchu lub zaszachowanie przez inna figure tego samego koloru w wyniku ruchu tej pierwszej
        if self.verify_check(self.board, self.turn):
            if figure.color == 'white':
                print('White player: Check!')
            else:
                print('Black player: Check!')
            self.change_turn()
            # sprawdzenie szach matu po zmianie tury
            if self.verify_checkmate(deepcopy(self.board), self.turn):
                self.gameover = True
                if self.turn == 'white':
                    print('Black player: Checkmate! Game over!')
                else:
                    print('White player: Checkmate! Game over!')
        else:
            self.change_turn()
            # sprawdzenie patu po zmianie tury
            if self.verify_stalemate(deepcopy(self.board), self.turn):
                self.gameover = True
                print('Stalemate! Draw!')

    def change_turn(self):
        self.selected = None
        self.valid_moves = []
        if self.turn == 'white':
            self.turn = 'black'
        else:
            self.turn = 'white'

    def get_valid_moves_for_pawns(self, board, figure):
        moves = []
        row = figure.row
        col = figure.col
        color = figure.color
        first_move = figure.first_move
        black_pawn = None
        white_pawn = None

        # sens sprawdzania mozliwosci bicia w przelocie jest tylko wtedy gdy ostatnia figura ktora dokonala ruchu to pionek odpowiedniego koloru
        if color == 'white' and self.last_move and self.last_move.type == 'pawn' and self.last_move.color == 'black' and self.last_move.move_counter == 1:
            black_pawn = self.last_move
        elif color == 'black' and self.last_move and self.last_move.type == 'pawn' and self.last_move.color == 'white' and self.last_move.move_counter == 1:
            white_pawn = self.last_move

        if color == 'white':
            if first_move:
                if board[row+1][col] == 0 and board[row+2][col] == 0:
                    moves.append((row+2, col))
            if black_pawn:
                if row == 4 and black_pawn.row == 4:
                    if black_pawn.col > 0 and black_pawn.col < 7:
                        if col - black_pawn.col == 1 or col - black_pawn.col == -1:
                            moves.append((5, black_pawn.col))
                            self.try_to_set_beating_in_flight()
                    if black_pawn.col == 0:
                        if col == 1:
                            moves.append((5, 0))
                            self.try_to_set_beating_in_flight()
                    if black_pawn.col == 7:
                        if col == 6:
                            moves.append((5, 7))
                            self.try_to_set_beating_in_flight()

            if board[row+1][col] == 0:
                moves.append((row+1, col))
        if color == 'white' and col > 0 and col < 7:
            if board[row+1][col+1] != 0 and board[row+1][col+1].color == 'black':
                moves.append((row+1, col+1))
            if board[row+1][col-1] != 0 and board[row+1][col-1].color == 'black':
                moves.append((row+1, col-1))
        if color == 'white' and col == 0:
            if board[row+1][col+1] != 0 and board[row+1][col+1].color == 'black':
                moves.append((row+1, col+1))
        if color == 'white' and col == 7:
            if board[row+1][col-1] != 0 and board[row+1][col-1].color == 'black':
                moves.append((row+1, col-1))

        if color == 'black':
            if first_move:
                if board[row-1][col] == 0 and board[row-2][col] == 0:
                    moves.append((row-2, col))
            if white_pawn:
                if row == 3 and white_pawn.row == 3:
                    if white_pawn.col > 0 and white_pawn.col < 7:
                        if col - white_pawn.col == 1 or col - white_pawn.col == -1:
                            moves.append((2, white_pawn.col))
                            self.try_to_set_beating_in_flight()
                    if white_pawn.col == 0:
                        if col == 1:
                            moves.append((2, 0))
                            self.try_to_set_beating_in_flight()
                    if white_pawn.col == 7:
                        if col == 6:
                            moves.append((2, 7))
                            self.try_to_set_beating_in_flight()

            if board[row-1][col] == 0:
                moves.append((row-1, col))
        if color == 'black' and col > 0 and col < 7:
            if board[row-1][col+1] != 0 and board[row-1][col+1].color == 'white':
                moves.append((row-1, col+1))
            if board[row-1][col-1] != 0 and board[row-1][col-1].color == 'white':
                moves.append((row-1, col-1))
        if color == 'black' and col == 0:
            if board[row-1][col+1] != 0 and board[row-1][col+1].color == 'white':
                moves.append((row-1, col+1))
        if color == 'black' and col == 7:
            if board[row-1][col-1] != 0 and board[row-1][col-1].color == 'white':
                moves.append((row-1, col-1))
        
        return moves

    def get_valid_moves_for_rooks(self, board, figure):
        moves = []
        row = figure.row
        col = figure.col
        color = figure.color
        dirs = ['right', 'left', 'up', 'down']
        if color == 'white':
            oppo_color = 'black'
        else:
            oppo_color = 'white'

        for dir in dirs:
            if dir == 'right':
                res_cols = COLS - col
                square_num = 1
                while square_num < res_cols:
                    if board[row][square_num + col] != 0 and board[row][square_num + col].color == color and square_num == 1:
                        break
                    if board[row][square_num + col] != 0 and board[row][square_num + col].color == color and square_num > 1:
                        moves.append((row, square_num + col - 1))
                        break
                    if board[row][square_num + col] != 0 and board[row][square_num + col].color == oppo_color:
                        moves.append((row, square_num + col))
                        break
                    if board[row][square_num + col] == 0:
                        moves.append((row, square_num + col))
                    square_num += 1
            if dir == 'left':
                res_cols = -1 - col
                square_num = -1
                while square_num > res_cols:
                    if board[row][square_num + col] != 0 and board[row][square_num + col].color == color and square_num == -1:
                        break
                    if board[row][square_num + col] != 0 and board[row][square_num + col].color == color and square_num < -1:
                        moves.append((row, square_num + col + 1))
                        break
                    if board[row][square_num + col] != 0 and board[row][square_num + col].color == oppo_color:
                        moves.append((row, square_num + col))
                        break
                    if board[row][square_num + col] == 0:
                        moves.append((row, square_num + col))
                    square_num -= 1
            if dir == 'down':
                res_rows = ROWS - row
                square_num = 1
                while square_num < res_rows:
                    if board[square_num + row][col] != 0 and board[square_num + row][col].color == color and square_num == 1:
                        break
                    if board[square_num + row][col] != 0 and board[square_num + row][col].color == color and square_num > 1:
                        moves.append((square_num + row - 1, col))
                        break
                    if board[square_num + row][col] != 0 and board[square_num + row][col].color == oppo_color:
                        moves.append((square_num + row, col))
                        break
                    if board[square_num + row][col] == 0:
                        moves.append((square_num + row, col))
                    square_num += 1
            if dir == 'up':
                res_rows = -1 - row
                square_num = -1
                while square_num > res_rows:
                    if board[square_num + row][col] != 0 and board[square_num + row][col].color == color and square_num == -1:
                        break
                    if board[square_num + row][col] != 0 and board[square_num + row][col].color == color and square_num < -1:
                        moves.append((square_num + row + 1, col))
                        break
                    if board[square_num + row][col] != 0 and board[square_num + row][col].color == oppo_color:
                        moves.append((square_num + row, col))
                        break
                    if board[square_num + row][col] == 0:
                        moves.append((square_num + row, col))
                    square_num -= 1
                      
        return moves

    def get_valid_moves_for_knights(self, board, figure):
        moves = []
        row = figure.row
        col = figure.col
        color = figure.color
        dirs = {'north_left': (row - 2, col - 1),
               'north_right': (row - 2, col + 1),
               'east_left': (row - 1, col + 2),
               'east_right': (row + 1, col + 2),
               'south_left': (row + 2, col + 1),
               'south_right': (row + 2, col - 1),
               'west_left': (row + 1, col - 2),
               'west_right': (row - 1, col - 2)}
        if color == 'white':
            oppo_color = 'black'
        else:
            oppo_color = 'white'

        for new_row, new_col in dirs.values():
            if (new_row >= 0 and new_row < ROWS) and (new_col >= 0 and new_col < COLS):
                if board[new_row][new_col] == 0 or board[new_row][new_col] != 0 and board[new_row][new_col].color == oppo_color:
                    moves.append((new_row, new_col))

        return moves

    def get_valid_moves_for_bishops(self, board, figure):
        moves = []
        row = figure.row
        col = figure.col
        color = figure.color
        dirs = ['right-up', 'left-up', 'right-down', 'left-down']
        if color == 'white':
            oppo_color = 'black'
        else:
            oppo_color = 'white'

        for dir in dirs:
            if dir == 'right-up':
                new_row = row - 1
                new_col = col + 1
                while new_row >= 0 and new_col < COLS:
                    if board[new_row][new_col] != 0 and board[new_row][new_col].color == color and new_row == row - 1:
                        break
                    if board[new_row][new_col] != 0 and board[new_row][new_col].color == color and new_row < row - 1:
                        moves.append((new_row + 1, new_col - 1))
                        break
                    if board[new_row][new_col] != 0 and board[new_row][new_col].color == oppo_color:
                        moves.append((new_row, new_col))
                        break
                    if board[new_row][new_col] == 0:
                        moves.append((new_row, new_col))
                    new_row -= 1
                    new_col += 1
            if dir == 'left-up':
                new_row = row - 1
                new_col = col - 1
                while new_row >= 0 and new_col >= 0:
                    if board[new_row][new_col] != 0 and board[new_row][new_col].color == color and new_row == row - 1:
                        break
                    if board[new_row][new_col] != 0 and board[new_row][new_col].color == color and new_row < row - 1:
                        moves.append((new_row + 1, new_col + 1))
                        break
                    if board[new_row][new_col] != 0 and board[new_row][new_col].color == oppo_color:
                        moves.append((new_row, new_col))
                        break
                    if board[new_row][new_col] == 0:
                        moves.append((new_row, new_col))
                    new_row -= 1
                    new_col -= 1
            if dir == 'right-down':
                new_row = row + 1
                new_col = col + 1
                while new_row < ROWS and new_col < COLS:
                    if board[new_row][new_col] != 0 and board[new_row][new_col].color == color and new_row == row + 1:
                        break
                    if board[new_row][new_col] != 0 and board[new_row][new_col].color == color and new_row > row + 1:
                        moves.append((new_row - 1, new_col - 1))
                        break
                    if board[new_row][new_col] != 0 and board[new_row][new_col].color == oppo_color:
                        moves.append((new_row, new_col))
                        break
                    if board[new_row][new_col] == 0:
                        moves.append((new_row, new_col))
                    new_row += 1
                    new_col += 1
            if dir == 'left-down':
                new_row = row + 1
                new_col = col - 1
                while new_row < ROWS and new_col >= 0:
                    if board[new_row][new_col] != 0 and board[new_row][new_col].color == color and new_row == row + 1:
                        break
                    if board[new_row][new_col] != 0 and board[new_row][new_col].color == color and new_row > row + 1:
                        moves.append((new_row - 1, new_col + 1))
                        break
                    if board[new_row][new_col] != 0 and board[new_row][new_col].color == oppo_color:
                        moves.append((new_row, new_col))
                        break
                    if board[new_row][new_col] == 0:
                        moves.append((new_row, new_col))
                    new_row += 1
                    new_col -= 1
                      
        return moves

    def get_valid_moves_for_kings(self, board, figure):
        moves = []
        row = figure.row
        col = figure.col
        color = figure.color
        dirs = {'north_west': (row - 1, col - 1),
               'north': (row - 1, col),
               'north_east': (row - 1, col + 1),
               'east': (row, col + 1),
               'south_east': (row + 1, col + 1),
               'south': (row + 1, col),
               'south_west': (row + 1, col - 1),
               'west': (row, col - 1)}
        if color == 'white':
            oppo_color = 'black'
        else:
            oppo_color = 'white'

        for new_row, new_col in dirs.values():
            if (new_row >= 0 and new_row < ROWS) and (new_col >= 0 and new_col < COLS):
                if board[new_row][new_col] == 0 or board[new_row][new_col] != 0 and board[new_row][new_col].color == oppo_color:
                    moves.append((new_row, new_col))

        return moves

    def verify_invalid_moves(self, temp_board, temp_fig, new_row, new_col):
        moves = []
        color = temp_fig.color
        if color == 'white':
            oppo_color = 'black'
        else:
            oppo_color = 'white'

        if temp_fig.type != 'king':
            for row in range(ROWS):
                for col in range(COLS):
                    if temp_board[row][col] != 0 and temp_board[row][col].color == color and temp_board[row][col].type == 'king':
                        king = temp_board[row][col]
            temp_board[temp_fig.row][temp_fig.col], temp_board[new_row][new_col] = 0, temp_board[temp_fig.row][temp_fig.col]
            temp_board[new_row][new_col].move(new_row, new_col)
        else:
            temp_board[temp_fig.row][temp_fig.col], temp_board[new_row][new_col] = 0, temp_board[temp_fig.row][temp_fig.col]
            temp_board[new_row][new_col].move(new_row, new_col)
            king = temp_board[new_row][new_col] # prawdopodobnie wciaz dziala tu deepcopy zaciagniety z argumentu, dlatego przypisanie musi odbyc sie PO KALKULACJI nowej pozycji

        for row in range(ROWS):
            for col in range(COLS):
                figure = temp_board[row][col]
                if figure != 0 and figure.color == oppo_color:
                    if figure.type == 'pawn':
                        moves += self.get_valid_moves_for_pawns(temp_board, figure)
                    elif figure.type == 'rook':
                        moves += self.get_valid_moves_for_rooks(temp_board, figure)
                    elif figure.type == 'knight':
                        moves += self.get_valid_moves_for_knights(temp_board, figure)
                    elif figure.type == 'bishop':
                        moves += self.get_valid_moves_for_bishops(temp_board, figure)
                    elif figure.type == 'queen':
                        moves += self.get_valid_moves_for_bishops(temp_board, figure) + self.get_valid_moves_for_rooks(temp_board, figure)
                    elif figure.type == 'king':
                        moves += self.get_valid_moves_for_kings(temp_board, figure)

        if (king.row, king.col) in moves:
            return True
        
        return False

    def verify_check(self, board, color):
        moves = []
        if color == 'white':
            oppo_color = 'black'
        else:
            oppo_color = 'white'

        for row in range(ROWS):
            for col in range(COLS):
                if board[row][col] != 0 and board[row][col].color == oppo_color and board[row][col].type == 'king':
                    oppo_king = board[row][col]

        for row in range(ROWS):
            for col in range(COLS):
                any_figure = board[row][col]
                if any_figure != 0 and any_figure.color == color:
                    if any_figure.type == 'pawn':
                        moves += self.get_valid_moves_for_pawns(board, any_figure)
                    elif any_figure.type == 'rook':
                        moves += self.get_valid_moves_for_rooks(board, any_figure)
                    elif any_figure.type == 'knight':
                        moves += self.get_valid_moves_for_knights(board, any_figure)
                    elif any_figure.type == 'bishop':
                        moves += self.get_valid_moves_for_bishops(board, any_figure)
                    elif any_figure.type == 'queen':
                        moves += self.get_valid_moves_for_bishops(board, any_figure) + self.get_valid_moves_for_rooks(board, any_figure)
                    elif any_figure.type == 'king':
                        moves += self.get_valid_moves_for_kings(board, any_figure)

        if (oppo_king.row, oppo_king.col) in moves:
            return True

        return False

    def verify_checkmate(self, temp_board, color):
        moves = []
        checks = 0
        all_moves = 0
        cancel_checkmate = []
        if color == 'white':
            oppo_color = 'black'
        else:
            oppo_color = 'white'

        for row in range(ROWS):
            for col in range(COLS):
                if temp_board[row][col] != 0 and temp_board[row][col].color == color and temp_board[row][col].type == 'king':
                    moves = self.get_valid_moves_for_kings(temp_board, temp_board[row][col])
                    for move in moves:
                        new_temp_board = deepcopy(temp_board)
                        all_moves += 1
                        new_row, new_col = move
                        new_temp_board[row][col], new_temp_board[new_row][new_col] = 0, new_temp_board[row][col]
                        new_temp_board[new_row][new_col].move(new_row, new_col)
                        if self.verify_check(new_temp_board, oppo_color):
                            checks += 1
                    if checks >= all_moves:
                        pass
                    else:
                        return False

        # jezeli krol nie jest w stanie sie sam obronic to jest sprawdzana mozliwosc obrony krola przez wszystkie pozostale figury
        for row in range(ROWS):
            for col in range(COLS):
                if temp_board[row][col] != 0 and temp_board[row][col].color == color and temp_board[row][col].type != 'king':
                    if temp_board[row][col].type == 'pawn':
                        moves = self.get_valid_moves_for_pawns(temp_board, temp_board[row][col])
                    elif temp_board[row][col].type == 'rook':
                        moves = self.get_valid_moves_for_rooks(temp_board, temp_board[row][col])
                    elif temp_board[row][col].type == 'knight':
                        moves = self.get_valid_moves_for_knights(temp_board, temp_board[row][col])
                    elif temp_board[row][col].type == 'bishop':
                        moves = self.get_valid_moves_for_bishops(temp_board, temp_board[row][col])
                    elif temp_board[row][col].type == 'queen':
                        moves = self.get_valid_moves_for_bishops(temp_board, temp_board[row][col]) + self.get_valid_moves_for_rooks(temp_board, temp_board[row][col])
                    
                    for move in moves:
                        new_temp_board = deepcopy(temp_board)
                        new_row, new_col = move
                        new_temp_board[row][col], new_temp_board[new_row][new_col] = 0, new_temp_board[row][col]
                        new_temp_board[new_row][new_col].move(new_row, new_col)
                        if self.verify_check(new_temp_board, oppo_color):
                            cancel_checkmate.append(False)
                        else:
                            cancel_checkmate.append(True)

        # wystarczy jeden ruch jakiejkolwiek innej figury ktora jest w stanie potencjalnie uratowac krola od szachu czyli tymbardziej szach matu
        if True in cancel_checkmate:
            return False

        return True

    def verify_stalemate(self, temp_board, color):
        moves = []
        checks = 0
        all_moves = 0
        cancel_stalemate = []
        if color == 'white':
            oppo_color = 'black'
        else:
            oppo_color = 'white'

        for row in range(ROWS):
            for col in range(COLS):
                if temp_board[row][col] != 0 and temp_board[row][col].color == color and temp_board[row][col].type == 'king':
                    moves = self.get_valid_moves_for_kings(temp_board, temp_board[row][col])
                    for move in moves:
                        new_temp_board = deepcopy(temp_board)
                        all_moves += 1
                        new_row, new_col = move
                        new_temp_board[row][col], new_temp_board[new_row][new_col] = 0, new_temp_board[row][col]
                        new_temp_board[new_row][new_col].move(new_row, new_col)
                        if self.verify_check(new_temp_board, oppo_color):
                            checks += 1
                    if checks >= all_moves:
                        pass
                    else:
                        return False

        # jezeli krol nie jest w stanie sie nigdzie ruszyc to jest sprawdzana mozliwosc ruchu przez wszystkie pozostale figury (o ile istnieja)
        for row in range(ROWS):
            for col in range(COLS):
                if temp_board[row][col] != 0 and temp_board[row][col].color == color and temp_board[row][col].type != 'king':
                    if temp_board[row][col].type == 'pawn':
                        moves = self.get_valid_moves_for_pawns(temp_board, temp_board[row][col])
                    elif temp_board[row][col].type == 'rook':
                        moves = self.get_valid_moves_for_rooks(temp_board, temp_board[row][col])
                    elif temp_board[row][col].type == 'knight':
                        moves = self.get_valid_moves_for_knights(temp_board, temp_board[row][col])
                    elif temp_board[row][col].type == 'bishop':
                        moves = self.get_valid_moves_for_bishops(temp_board, temp_board[row][col])
                    elif temp_board[row][col].type == 'queen':
                        moves = self.get_valid_moves_for_bishops(temp_board, temp_board[row][col]) + self.get_valid_moves_for_rooks(temp_board, temp_board[row][col])
                    if not moves:
                        cancel_stalemate.append(False)
                    else:
                        cancel_stalemate.append(True)

        # wystarczy ruch jakiejkolwiek innej figury niz krol zeby anulowac potecjalny pat
        if True in cancel_stalemate:
            return False

        return True

    def castling(self, board, row, col):
        self.selected = None
        self.valid_moves = []
        if self.turn == 'white':
            oppo_color = 'black'
        else:
            oppo_color = 'white'

        if board[row][col] == 0 or board[row][col] != 0 and (board[row][col].color != self.turn or board[row][col].color == self.turn and board[row][col].type != 'king' and board[row][col].type != 'rook'):
            self.selected_king_for_castling = None
            self.selected_rook_for_castling = None

        if board[row][col] != 0 and board[row][col].color == self.turn:
            if board[row][col].type == 'king':
                self.selected_king_for_castling = board[row][col]
                self.valid_moves = [(row, 0), (row, 7)]
            elif board[row][col].type == 'rook':
                self.selected_rook_for_castling = board[row][col]
                self.valid_moves = [(row, 4)]

        if self.selected_king_for_castling and self.selected_rook_for_castling:
            king = self.selected_king_for_castling
            rook = self.selected_rook_for_castling
            if rook.first_move and king.first_move and not self.verify_check(board, oppo_color):
                if rook.col == 0:
                    if board[row][1] == 0 and board[row][2] == 0 and board[row][3] == 0:
                        if not self.verify_invalid_moves(deepcopy(board), deepcopy(king), row, 3):
                            if not self.verify_invalid_moves(deepcopy(board), deepcopy(king), row, 2):
                                self.move(king, row, 2)
                                self.change_turn()
                                self.move(rook, row, 3)
                                self.selected_king_for_castling = None
                                self.selected_rook_for_castling = None
                                return
                elif rook.col == 7:
                    if board[row][5] == 0 and board[row][6] == 0:
                        if not self.verify_invalid_moves(deepcopy(board), deepcopy(king), row, 5):
                            if not self.verify_invalid_moves(deepcopy(board), deepcopy(king), row, 6):
                                self.move(king, row, 6)
                                self.change_turn()
                                self.move(rook, row, 5)
                                self.selected_king_for_castling = None
                                self.selected_rook_for_castling = None
                                return
            
            self.selected_king_for_castling = None
            self.selected_rook_for_castling = None
            if self.turn == 'white':
                print('Black player: Cannot perform a castling!')
            else:
                print('White player: Cannot perform a castling!')

    def try_to_set_beating_in_flight(self):
        if self.beating_in_flight_can_be_set:
            self.beating_in_flight = True
