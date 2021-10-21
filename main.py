from state import State, State_2
import time
from importlib import import_module

# Player 1
win = 0
draw = 0
lose = 0

def main(player_X, player_O, rule = 1):
    global win, draw, lose
    dict_player = {1: 'X', -1: 'O'}
    if rule == 1:
        cur_state = State()
    else:
        cur_state = State_2()
    turn = 1    

    limit = 81
    remain_time_X = 120
    remain_time_O = 120

    player_1 = import_module(player_X)
    player_2 = import_module(player_O)


    while turn <= limit:
        # print("turn:", turn, end='\n\n')
        if cur_state.game_over:
            # print("winner:", dict_player[cur_state.player_to_move * -1])
            if cur_state.player_to_move == -1:
                win += 1
            return

        start_time = time.time()
        if cur_state.player_to_move == 1:
            new_move = player_1.select_move(cur_state, remain_time_X)
            elapsed_time = time.time() - start_time
            remain_time_X -= elapsed_time
        else:
            new_move = player_2.select_move(cur_state, remain_time_O)
            elapsed_time = time.time() - start_time
            remain_time_O -= elapsed_time

        if new_move == None:
            return

        if remain_time_X < 0 or remain_time_O < 0:
            # print("out of time")
            # print("winner:", dict_player[cur_state.player_to_move * -1])
            if cur_state.player_to_move == -1:
                win += 1
            return

        if elapsed_time > 10.0:
            # print("elapsed time:", elapsed_time)
            # print("winner: ", dict_player[cur_state.player_to_move * -1])
            if cur_state.player_to_move == -1:
                win += 1
            return

        cur_state.act_move(new_move)
        # print(cur_state)

        turn += 1

    draw += 1
    # print("X:", cur_state.count_X)
    # print("O:", cur_state.count_O)


cnt = 50
for i in range(cnt):
    print("Phrase {}:".format(i))
    main('_1910663_1914637_1914405', 'random_agent')

print("          | Win | Lose | Draw")
print("Player 1  | {} | {} | {}".format(win, cnt - win - draw, draw))
print("Player 2  | {} | {} | {}".format(cnt - win - draw, win, draw))


 
