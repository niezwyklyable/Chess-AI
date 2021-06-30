
import pygame
from copy import deepcopy
from .constants import ROWS, COLS
from .queen import Queen

def remove(board, temp_dict, row, col):
    if board[row][col].color == 'white':
        if board[row][col].type == 'pawn':
            temp_dict['white_pawns'] -= 1
        elif board[row][col].type == 'rook':
            temp_dict['white_rooks'] -= 1
        elif board[row][col].type == 'knight':
            temp_dict['white_knights'] -= 1
        elif board[row][col].type == 'bishop':
            temp_dict['white_bishops'] -= 1
        elif board[row][col].type == 'queen':
            temp_dict['white_queens'] -= 1
    elif board[row][col].color == 'black':
        if board[row][col].type == 'pawn':
            temp_dict['black_pawns'] -= 1
        elif board[row][col].type == 'rook':
            temp_dict['black_rooks'] -= 1
        elif board[row][col].type == 'knight':
            temp_dict['black_knights'] -= 1
        elif board[row][col].type == 'bishop':
            temp_dict['black_bishops'] -= 1
        elif board[row][col].type == 'queen':
            temp_dict['black_queens'] -= 1

    return temp_dict

def get_all_moves(board, color, game, temp_dict):
    moves = {}
    valid_moves = []
    if color == 'white':
        oppo_color = 'black'
    else:
        oppo_color = 'white'

    for row in range(ROWS):
        for col in range(COLS):
            any_figure = board[row][col]
            if any_figure != 0 and any_figure.color == color:
                valid_moves = []
                if any_figure.type == 'pawn':
                    valid_moves = game.get_valid_moves_for_pawns(board, any_figure)
                elif any_figure.type == 'rook':
                    valid_moves = game.get_valid_moves_for_rooks(board, any_figure)
                elif any_figure.type == 'knight':
                    valid_moves = game.get_valid_moves_for_knights(board, any_figure)
                elif any_figure.type == 'bishop':
                    valid_moves = game.get_valid_moves_for_bishops(board, any_figure)
                elif any_figure.type == 'queen':
                    valid_moves = game.get_valid_moves_for_bishops(board, any_figure) + game.get_valid_moves_for_rooks(board, any_figure)
                elif any_figure.type == 'king':
                    valid_moves = game.get_valid_moves_for_kings(board, any_figure)
                
                for move in valid_moves:
                    new_temp_board = deepcopy(board)
                    new_row, new_col = move
                    if not game.verify_invalid_moves(deepcopy(board), deepcopy(any_figure), new_row, new_col):
                        if new_temp_board[new_row][new_col] != 0:
                            new_temp_dict = remove(new_temp_board, deepcopy(temp_dict), new_row, new_col)
                            if new_temp_board[new_row][new_col].checking:
                                new_temp_dict['checking_figure_is_beaten'] = True
                        else:
                            new_temp_dict = deepcopy(temp_dict)
                        new_temp_board[row][col], new_temp_board[new_row][new_col] = 0, new_temp_board[row][col]
                        new_temp_board[new_row][new_col].move(new_row, new_col)
                        # promocja piona - nagroda
                        if new_temp_board[new_row][new_col].type == 'pawn' and new_temp_board[new_row][new_col].color == 'white' and new_temp_board[new_row][new_col].row == 7:
                            new_temp_board[new_row][new_col] = Queen(new_row, new_col, 'white')
                            new_temp_dict['white_queens'] += 2
                        if new_temp_board[new_row][new_col].type == 'pawn' and new_temp_board[new_row][new_col].color == 'black' and new_temp_board[new_row][new_col].row == 0:
                            new_temp_board[new_row][new_col] = Queen(new_row, new_col, 'black')
                            new_temp_dict['black_queens'] += 2
                        # sprawdzenie szachu i ewentualna nagroda ale tylko dla max playera
                        if game.verify_check(new_temp_board, color):
                            if color == 'black':
                                new_temp_board[new_row][new_col].checking = True
                                new_temp_dict['white_king'] -= 1
                            # sprawdzenie szach matu i ewentualna nagroda
                            if game.verify_checkmate(deepcopy(new_temp_board), oppo_color):
                                new_temp_dict['gameover'] = True
                                if color == 'white':
                                    new_temp_dict['white_checkmate_reward'] += 1
                                else:
                                    new_temp_dict['black_checkmate_reward'] += 1
                        else:
                            # sprawdzenie patu
                            if game.verify_stalemate(deepcopy(new_temp_board), oppo_color):
                                new_temp_dict['gameover'] = True
                        moves.update({(any_figure, new_row, new_col): (new_temp_board, new_temp_dict)})
                        # nie wiem czy any_figure nie powinno byc w deepcopy ale chyba nie musi

    return moves

def evaluate_reward(temp_dict):
    if not temp_dict['checking_figure_is_beaten']:
        reward = 1.0 * (temp_dict['black_pawns'] - temp_dict['white_pawns']) + \
            2.0 * (temp_dict['black_rooks'] - temp_dict['white_rooks']) + \
            2.0 * (temp_dict['black_knights'] - temp_dict['white_knights']) + \
            2.0 * (temp_dict['black_bishops'] - temp_dict['white_bishops']) + \
            3.0 * (temp_dict['black_queens'] - temp_dict['white_queens']) + \
            1.5 * (temp_dict['black_king'] - temp_dict['white_king']) + \
            100 * (temp_dict['black_checkmate_reward'] - temp_dict['white_checkmate_reward'])
    else:
        reward = 1.0 * (temp_dict['black_pawns'] - temp_dict['white_pawns']) + \
            2.0 * (temp_dict['black_rooks'] - temp_dict['white_rooks']) + \
            2.0 * (temp_dict['black_knights'] - temp_dict['white_knights']) + \
            2.0 * (temp_dict['black_bishops'] - temp_dict['white_bishops']) + \
            3.0 * (temp_dict['black_queens'] - temp_dict['white_queens']) + \
            0.5 * (temp_dict['black_king'] - temp_dict['white_king']) + \
            100 * (temp_dict['black_checkmate_reward'] - temp_dict['white_checkmate_reward'])

    return reward

def minimax(board, depth, max_player, game, temp_dict):
    if depth == 0 or temp_dict['gameover']:
        best_figure = None
        new_row = 0
        new_col = 0
        #print('first')
        #print(temp_dict)
        return evaluate_reward(temp_dict), best_figure, new_row, new_col

    if max_player:
        maxEval = float('-inf')
        for moved_figure, move in get_all_moves(board, 'black', game, temp_dict).items():
            reward = minimax(move[0], depth - 1, False, game, move[1])[0]
            maxEval = max(maxEval, reward)
            #print('any_figure:', moved_figure)
            if maxEval == reward:
                best_figure, new_row, new_col = moved_figure
    
        #print('max_player')
        #print('reward:', reward)
        #print('maxEval:', maxEval)
        #print('best_figure:', best_figure, best_figure.row, best_figure.col, new_row, new_col)
        return maxEval, best_figure, new_row, new_col

    else:
        minEval = float('inf')
        for moved_figure, move in get_all_moves(board, 'white', game, temp_dict).items():
            reward = minimax(move[0], depth - 1, True, game, move[1])[0]
            minEval = min(minEval, reward)
            #print('any_figure:', moved_figure)
            if minEval == reward:
                best_figure, new_row, new_col = moved_figure
                
        #print('min_player')
        #print('reward:', reward)
        #print('minEval:', minEval)
        #print('best_figure:', best_figure, best_figure.row, best_figure.col, new_row, new_col)
        return minEval, best_figure, new_row, new_col
