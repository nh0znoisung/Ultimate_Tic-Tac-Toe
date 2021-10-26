from typing import ValuesView
import numpy as np
import math
import random
from copy import deepcopy
from state import State

maxDepth = 5

def select_move(cur_state, remain_time): # return move in valid_moves -> UltimateTTT + Time ups
    (best_move, cur_cost) = minimaxAB(cur_state, 0, -math.inf, math.inf)
    return best_move



def minimaxAB(cur_state: State, depth, alpha, beta): # return State in Ultimate
    # print("Hello World 1")
    
    if depth == maxDepth:
        return (None, heuristic_Cost(cur_state))
    # print("Hello World 3")

    valid_moves = cur_state.get_valid_moves
    #random.shuffle(valid_moves) # random the list for the fair chance
    # print("Hello World 4")

    if cur_state.player_to_move == 1:
        #Maximizing player
        best_move = None
        v = -np.inf
        for move in valid_moves:
            new_state = deepcopy(cur_state)
            new_state.act_move(move)
            (new_move, new_cost) = minimaxAB(new_state, depth + 1, alpha, beta)
            v = max(v, new_cost)

            if (v >= beta):
                best_move = move
                return (best_move,v)

            alpha = max(alpha, v)

        return (best_move, v)

    elif cur_state.player_to_move == -1:
        #Minimizing player
        best_move = None
        v = np.inf
        for move in valid_moves:
            new_state = deepcopy(cur_state)
            new_state.act_move(move)
            (new_move, new_cost) = minimaxAB(new_state, depth + 1, alpha, beta)
            v = min(v, new_cost)

            if (v <= alpha):
                best_move = move
                return (best_move,v)

            beta = min(beta,v)

        # print(cost_block(cur_state))
        return (best_move, v)

def calc_twos(local_board, value: int, player, opponent):
    change = 0
    local_board = np.reshape(local_board,(3,3))

    for y in range(len(local_board)):
        to_change = 0

        if local_board[y][0] == local_board[y][1] and local_board[y][2] == 0:
            to_change = value

        if local_board[y][1] == local_board[y][2] and local_board[y][0] == 0:
            to_change = value
        
        if local_board[y][2] == local_board[y][0] and local_board[y][1] == 0:
            to_change = value
        
        if player in (local_board[y][1], local_board[y][2]):
            change += to_change
        
        if opponent in (local_board[y][1], local_board[y][2]):
            change -= to_change
    
    for x in range(len(local_board[0])):
        to_change = 0

        if local_board[0][x] == local_board[1][x] and local_board[2][x] == 0:
            to_change = value

        if local_board[1][x] == local_board[2][x] and local_board[0][x] == 0:
            to_change  = value
        
        if local_board[2][x] == local_board[0][x] and local_board[1][x] == 0:
            to_change = value
        
        if player in (local_board[1][x], local_board[2][x]):
            change += to_change
        
        if opponent in (local_board[1][x], local_board[2][x]):
            change -= to_change

    to_change = 0

    if local_board[0][0] == local_board[1][1] and local_board[2][2] == 0:
        to_change = value
    if local_board[1][1] == local_board[2][2] and local_board[0][0] == 0:
        to_change = value
    if local_board[0][0] == local_board[2][2] and local_board[1][1] == 0:
        to_change = value
    
    if player in (local_board[0,0], local_board[2,2]):
        change += to_change
    if opponent in (local_board[0,0],local_board[2,2]):
        change -= to_change
    
    if local_board[2][0] == local_board[1][1] and local_board[0][2] == 0:
        to_change = value
    if local_board[2][0] == local_board[0][2] and local_board[1][1] == 0:
        to_change = value

    if player in (local_board[2,0], local_board[0,2]):
        change += to_change
    if opponent in (local_board[2,0],local_board[0,2]):
        change -= to_change
    
    return change

def calc_block(local_board, value: int, player, opponent):
    change = 0
    #local_board = np.reshape(local_board(3,3))
    for y in range(len(local_board)):
        to_change = 0

        if local_board[y][0] == local_board[y][1] == opponent and local_board[y][2] == player:
            to_change = value

        if local_board[y][1] == local_board[y][2] == opponent and local_board[y][0] == player:
            to_change = value
        
        if local_board[y][0] == local_board[y][2] == opponent and local_board[y][1] == player:
            to_change = value

        change += to_change
    
    for x in range(len(local_board[0])):
        to_change = value

        if local_board[0][x] == local_board[1][x] == opponent and local_board[2][x] == player:
            to_change = value
        if local_board[0][x] == local_board[2][x] == opponent and local_board[1][x] == player:
            to_change = value
        if local_board[1][x] == local_board[2][x] == opponent and local_board[0][x] == player:
            to_change = value
        change += to_change

    to_change = 0

    if local_board[0][0] == local_board[1][1] == opponent and local_board[2][2] == player:
        to_change = value
    if local_board[0][0] == local_board[2][2] == opponent and local_board[1][1] == player:
        to_change = value
    if local_board[1][1] == local_board[2][2] == opponent and local_board[0][0] == player:
        to_change = value
    
    change += to_change

    if local_board[2][0] == local_board[1][1] == opponent and local_board[0][2] == player:
        to_change = value
    if local_board[2][0] == local_board[0][2] == opponent and local_board[1][1] == player:
        to_change = value
    if local_board[1][1] == local_board[0][2] == opponent and local_board[2][0] == player:
        to_change = value

    change += to_change

    return change

def heuristic_Cost(cur_state: State, value_state = None, turn_amount = 0):
    if value_state is None:
        value_state = {'won 1':100, 'won 2 in a row': 200, 'won game': math.inf, '2 in a row': 5, 'blocked 2':12
        , 'won block 2': 120}
    score = 0
    player = cur_state.player_to_move
    opponent = -1 * player

    won_boards = cur_state.global_cells.reshape(3,3)
    
    # Calculate score for individual boards based on the number of "useful 2" they have
    for large_y in range(len(won_boards)):
        for large_x in range(len(won_boards[large_y])):
            local_board = cur_state.blocks[large_y*3+large_x]
            if (won_boards[large_y][large_x] != 0):
                continue

            score += calc_twos(local_board, value_state['won 2 in a row'],player,opponent)

    # Check for single won boards
    for y in range(len(won_boards)):
        for x in range(len(won_boards[y])):
            if (won_boards[y][x] == player):
                score += value_state['won 1']
            
            if (won_boards[y][x] == opponent):
                score -= value_state['won 1']
    
    score += calc_twos(won_boards, value_state['won 2 in a row'],player,opponent)

    if cur_state.game_result(won_boards) == player:
        return np.inf 
    elif cur_state.game_result(won_boards) == opponent:
        return -np.inf

    for y in range(len(won_boards)):
        for x in range(len(won_boards[y])):
            score += calc_block(cur_state.blocks[y*3+x], value_state['blocked 2'], player, opponent)
            score -= calc_block(cur_state.blocks[y*3+x], value_state['blocked 2'], opponent, player)

    score += calc_block(won_boards, value_state['won block 2'], player, opponent)
    score -= calc_block(won_boards, value_state['won block 2'], opponent, player)

    return score