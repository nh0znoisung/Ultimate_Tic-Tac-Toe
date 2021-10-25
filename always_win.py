from state import State, UltimateTTT_Move
import numpy as np


def getBlock(x, y):
    return 3*x + y


def first_move(cur_state: State):
    if cur_state.blocks[4, 1, 1] == 0:
        global i
        i = 1
        return UltimateTTT_Move(4, 1, 1, cur_state.player_to_move)
    else:
        if i < 8:
            b = getBlock(cur_state.previous_move.x, cur_state.previous_move.y)
            i += 1
            return UltimateTTT_Move(b, 1, 1, cur_state.player_to_move)
        elif i == 8:
            global x
            global y
            x = cur_state.previous_move.x
            y = cur_state.previous_move.y
            i += 1
            return UltimateTTT_Move(getBlock(x, y), x, y, cur_state.player_to_move)
        else:
            if cur_state.previous_move.x == 1 and cur_state.previous_move.y == 1:
                cur_state.free_move = True
                op_x = 2 - x
                op_y = 2 - y
                b = getBlock(op_x, op_y)
                if cur_state.blocks[b, x, y] == 0:
                    return UltimateTTT_Move(b, x, y, cur_state.player_to_move)
                else:
                    return UltimateTTT_Move(b, op_x, op_y, cur_state.player_to_move)
            else:
                b = getBlock(cur_state.previous_move.x,
                             cur_state.previous_move.y)
                if cur_state.blocks[b, x, y] == 0:
                    return UltimateTTT_Move(b, x, y, cur_state.player_to_move)
                else:
                    return UltimateTTT_Move(b, 2 - x, 2 - y, cur_state.player_to_move)


def select_move(cur_state: State, remain_time):
    # valid_moves = cur_state.get_valid_moves
    # if len(valid_moves) != 0:
    #     a = np.random.choice(valid_moves)
    #     print(a)
    #     return a
    # return None
    return first_move(cur_state)
