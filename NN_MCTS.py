import tensorflow as tf
from keras.models import load_model
import numpy as np
from state import UltimateTTT_Move

MCTS = True
model_path = "model_2.h5"
mcts_search = 400
# cpuct = 2

nn = load_model(model_path)

def state_to_array(state):
    array = []
    for i in range(9):
        array.append(state.blocks[i][0])
        array.append(state.blocks[i][1])
        array.append(state.blocks[i][2])

    nparray = np.array(array)
    nparray = np.where(nparray==0, 0.1, nparray) #0.1
    return nparray

def ultimate_to_array(u):
    poss = []
    for ulti in u:
        poss.append(ulti.index_local_board * 9 + ulti.x * 3 + ulti.y)
    return poss

def number_to_ultimate(n, cur_state):
    return UltimateTTT_Move(int(n/9), int((n%9)/3), n%3, cur_state.player_to_move)

def select_move(cur_state, remain_time): # return move in valid_moves -> UltimateTTT + Time ups
    # if MCTS:
        # too slow
        # policy = get_action_probs(board, -1, mini_board)
        # policy = policy / np.sum(policy)

    # more faster 
    policy, value = nn.predict(state_to_array(cur_state).reshape(1,9,9))
    valid_moves = cur_state.get_valid_moves

    if (len(valid_moves) == 0):
        return None
    possibleA = ultimate_to_array(valid_moves)

    valids = np.zeros(81)
    np.put(valids,possibleA,1)
    policy = policy.reshape(81) * valids
    policy = policy / np.sum(policy)

    action = np.argmax(policy)

    return number_to_ultimate(action, cur_state)

