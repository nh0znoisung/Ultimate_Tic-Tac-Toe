import numpy as np
import math
import random
from copy import deepcopy

maxDepth = 3

def select_move(cur_state, remain_time): # return move in valid_moves -> UltimateTTT + Time ups
    (best_move, cur_cost) = minimaxAB(cur_state, 0, -math.inf, math.inf)
    return best_move


def minimaxAB(cur_state, depth, alpha, beta): # return State in Ultimate
    # print("Hello World 1")

    if cur_state.game_over:
        if depth % 2 == 0:
            return (None, -math.inf)
        else:
            return (None, math.inf)
    # print("Hello World 2")
    
    if depth == maxDepth:
        return (None, cost(cur_state))
    # print("Hello World 3")


    valid_moves = cur_state.get_valid_moves
    random.shuffle(valid_moves) # random the list for the fair chance
    # print("Hello World 4")

    if cur_state.player_to_move == 1:
        #Maximizing player
        best_move = None

        for move in valid_moves:
            new_state = deepcopy(cur_state)
            new_state.act_move(move)
            (new_move, new_cost) = minimaxAB(new_state, depth + 1, alpha, beta)

            if new_cost > alpha:
                alpha = new_cost
                best_move = move

            if alpha >= beta:
                break
        return (best_move, alpha)

    elif cur_state.player_to_move == -1:
        #Minimizing player
        best_move = None

        for move in valid_moves:
            new_state = deepcopy(cur_state)
            new_state.act_move(move)
            (new_move, new_cost) = minimaxAB(new_state, depth + 1, alpha, beta)
            
            if new_cost < beta:
                beta = new_cost
                best_move = move

            if alpha >= beta:
                break   
        # print(cost_block(cur_state))
        return (best_move, beta)

def cost(cur_state):
    return 2

# def cost(cur_state):
#     return cost_player(cur_state, 1) - cost_player(cur_state, -1)

# def cost_player(cur_state, turn):
#     return 0

# # def cost_block(cur_state, turn):
# #     # Count how many way we can win this game
# #     return 0

# def cost_block(cur_state):
#     index_local_board = cur_state.previous_move.x * 3 + cur_state.previous_move.y
    
#     local_board = cur_state.blocks[index_local_board].reshape(9)
#     count = 0
#     i = 0
#     for p in range(0,3):
#         if(local_board[i]!= -1*cur_state.player_to_move and local_board[i+1]!= -1*cur_state.player_to_move and local_board[i+2]!= -1*cur_state.player_to_move):
#             count +=1
#         i += 3
#     for i in range(0,3):
#         if(local_board[i]!= -1*cur_state.player_to_move and local_board[i+3]!= -1*cur_state.player_to_move and local_board[i+6]!= -1*cur_state.player_to_move):
#             count +=1
#     if(local_board[0]!= -1*cur_state.player_to_move and local_board[4]!= -1*cur_state.player_to_move and local_board[8]!= -1*cur_state.player_to_move):
#         count += 1
#     if(local_board[2]!= -1*cur_state.player_to_move and local_board[4]!= -1*cur_state.player_to_move and local_board[6]!= -1*cur_state.player_to_move):
#         count += 1
#     return count

# self.global_cells = np.zeros(9)
# self.blocks = np.array([np.zeros((3, 3)) for x in range(9)])