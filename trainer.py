import tensorflow as tf
import keras
from keras import layers
from keras.models import Model
from keras import models
from tensorflow.keras.optimizers import Adam
import numpy as np
import math
from collections import deque
import os
import time
from datetime import datetime
import h5py
import copy
from os import walk
import pickle


""" 
Functions for game board
"""


def get_empty_board():
    board = []
    for i in range(9):
        board.append([[" ", " ", " "],
                      [" ", " ", " "],
                      [" ", " ", " "]])
    return board


def print_board(totalBoard):
    firstRow = ""
    secondRow = ""
    thirdRow = ""

    # Takes each board, saves the rows in a variable, then prints the variables
    for boardIndex in range(len(totalBoard)):
        firstRow = firstRow + "|" + " ".join(totalBoard[boardIndex][0]) + "|"
        secondRow = secondRow + "|" + " ".join(totalBoard[boardIndex][1]) + "|"
        thirdRow = thirdRow + "|" + " ".join(totalBoard[boardIndex][2]) + "|"

        # if 3 boards have been collected, then it prints the boards out and resets the variables (firstRow, secondRow, etc.)
        if boardIndex > 1 and (boardIndex + 1) % 3 == 0:
            print(firstRow)
            print(secondRow)
            print(thirdRow)
            print("---------------------")
            firstRow = ""
            secondRow = ""
            thirdRow = ""


def possiblePos(board, subBoard):

    if subBoard == 9:
        return range(81)

    possible = []

    # otherwise, finds all available spaces in the subBoard
    if board[subBoard][1][1] != 'x' and board[subBoard][1][1] != 'o':
        for row in range(3):
            for coloumn in range(3):
                if board[subBoard][row][coloumn] == " ":
                    possible.append((subBoard * 9) + (row * 3) + coloumn)
        if len(possible) > 0:
            return possible

    # if the subboard has already been won, it finds all available spaces on the entire board
    for mini in range(9):
        if board[mini][1][1] == "x" or board[mini][1][1] == "o":
            continue
        for row in range(3):
            for coloumn in range(3):
                if board[mini][row][coloumn] == " ":
                    possible.append((mini * 9) + (row * 3) + coloumn)

    return possible


def move(board, action, player):

    if player == 1:
        turn = 'X'
    if player == -1:
        turn = "O"

    bestPosition = []

    bestPosition.append(int(action / 9))
    remainder = action % 9
    bestPosition.append(int(remainder/3))
    bestPosition.append(remainder % 3)

    # place piece at position on board
    board[bestPosition[0]][bestPosition[1]][bestPosition[2]] = turn

    emptyMiniBoard = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]

    wonBoard = False
    win = False
    mini = board[bestPosition[0]]
    subBoard = bestPosition[0]
    x = bestPosition[1]
    y = bestPosition[2]

    # check for win on verticle
    if mini[0][y] == mini[1][y] == mini[2][y]:
        board[subBoard] = emptyMiniBoard
        board[subBoard][1][1] = turn.lower()
        wonBoard = True

    # check for win on horozontal
    if mini[x][0] == mini[x][1] == mini[x][2]:
        board[subBoard] = emptyMiniBoard
        board[subBoard][1][1] = turn.lower()
        wonBoard = True

    # check for win on negative diagonal
    if x == y and mini[0][0] == mini[1][1] == mini[2][2]:
        board[subBoard] = emptyMiniBoard
        board[subBoard][1][1] = turn.lower()
        wonBoard = True

    # check for win on positive diagonal
    if x + y == 2 and mini[0][2] == mini[1][1] == mini[2][0]:
        board[subBoard] = emptyMiniBoard
        board[subBoard][1][1] = turn.lower()
        wonBoard = True

    # set new subBoard
    newsubBoard = (bestPosition[1] * 3) + bestPosition[2]

    # if the subBoard was won, checking whether the entire board is won as well
    if wonBoard == True:
        win = checkWinner(board, subBoard, turn)

    # if win:
    #    print ("won game!")
      #  print_board(board)

    return board, newsubBoard, win


def checkWinner(board, winningSubBoard, turn):

    # getting coordinates of winning subBoard
    for i in range(3):
        if (winningSubBoard - i) % 3 == 0:
            row = int((winningSubBoard - i) / 3)
            winningSubBoardCoordinate = [row, i]
            break

    # making winning subBoard using just centre pieces
    winningBoard = [
        [board[0][1][1], board[1][1][1], board[2][1][1]],
        [board[3][1][1], board[4][1][1], board[5][1][1]],
        [board[6][1][1], board[7][1][1], board[8][1][1]]
    ]

    # horozontal wins
    if turn.lower() == winningBoard[winningSubBoardCoordinate[0]][0] == winningBoard[winningSubBoardCoordinate[0]][1] == winningBoard[winningSubBoardCoordinate[0]][2]:
        return True
    # vertical wins
    elif turn.lower() == winningBoard[0][winningSubBoardCoordinate[1]] == winningBoard[1][winningSubBoardCoordinate[1]] == winningBoard[2][winningSubBoardCoordinate[1]]:
        return True
    # top left to bottom right diagonal
    elif turn.lower() == winningBoard[0][0] == winningBoard[1][1] == winningBoard[2][2]:
        return True
    # bottom left to top right diagonal
    elif turn.lower() == winningBoard[2][0] == winningBoard[1][1] == winningBoard[0][2]:
        return True
    else:
        return False


""" 
---------------------------------------------------------

Stuff to actually train the model

---------------------------------------------------------
"""


# hyperparameters
train_episodes = 100
mcts_search = 600
n_pit_network = 20
playgames_before_training = 3
cpuct = 4
training_epochs = 20
learning_rate = 0.001
save_model_path = 'models_def'
cwd = os.getcwd()

# initializing search tree
Q = {}  # state-action values
Nsa = {}  # number of times certain state-action pair has been visited
Ns = {}   # number of times state has been visited
W = {}  # number of total points collected after taking state action pair
P = {}  # initial predicted probabilities of taking certain actions in state


# need to impliment get board function

def fill_winning_boards(board):

    # takes in a board in its normal state, and converts all suboards that have been won to be filled with the winning player's piece

    new_board = []
    for suboard in board:
        if suboard[1][1] == 'x':
            new_board.append(
                [["X", "X", "X"], ["X", "X", "X"], ["X", "X", "X"]])
        elif suboard[1][1] == 'o':
            new_board.append(
                [["O", "O", "O"], ["O", "O", "O"], ["O", "O", "O"]])
        else:
            new_board.append(suboard)
    return new_board


def letter_to_int(letter, player):
    # based on the letter in a box in the board, replaces 'X' with 1 and 'O' with -1
    if letter == 'v':
        return 0.1
    elif letter == " ":
        return 0
    elif letter == "X":
        return 1 * player
    elif letter == "O":
        return -1 * player


def board_to_array(boardreal, mini_board, player):

    # makes copy of board, so that the original board does not get changed
    board = copy.deepcopy(boardreal)

    # takes a board in its normal state, and returns a 9x9 numpy array, changing 'X' = 1 and 'O' = -1
    # also places a 0.1 in all valid board positions

    board = fill_winning_boards(board)
    tie = True

    # if it is the first turn, then all of the cells are valid moves
    if mini_board == 9:
        return np.full((9, 9), 0.1)

    # replacing all valid positions with 'v'
    # checking whether all empty values on the board are valid
    if board[mini_board][1][1] != 'x' or board[mini_board][1][1] != 'o':
        for line in range(3):
            for item in range(3):
                if board[mini_board][line][item] == " ":
                    board[mini_board][line][item] = 'v'
                    tie = False
    # if not, then replacing empty cells in mini board with 'v'
    else:
        for suboard in range(9):
            for line in range(3):
                for item in range(3):
                    if board[suboard][line][item] == " ":
                        board[suboard][line][item] = 'v'

    # if the miniboard ends up being a tie
    if tie:
        for suboard in range(9):
            for line in range(3):
                for item in range(3):
                    if board[suboard][line][item] == " ":
                        board[suboard][line][item] = 'v'

    array = []
    firstline = []
    secondline = []
    thirdline = []

    for suboardnum in range(len(board)):

        for item in board[suboardnum][0]:
            firstline.append(letter_to_int(item, player))

        for item in board[suboardnum][1]:
            secondline.append(letter_to_int(item, player))

        for item in board[suboardnum][2]:
            thirdline.append(letter_to_int(item, player))

        if (suboardnum + 1) % 3 == 0:
            array.append(firstline)
            array.append(secondline)
            array.append(thirdline)
            firstline = []
            secondline = []
            thirdline = []

    nparray = np.array(array)

    return nparray


def mcts(s, current_player, mini_board):

    if mini_board == 9:
        possibleA = range(81)
    else:
        possibleA = possiblePos(s, mini_board)

    sArray = board_to_array(s, mini_board, current_player)
    sTuple = tuple(map(tuple, sArray))

    if len(possibleA) > 0:
        if sTuple not in P.keys():

            policy, v = nn.predict(sArray.reshape(1, 9, 9))
            v = v[0][0]
            valids = np.zeros(81)
            np.put(valids, possibleA, 1)
            policy = policy.reshape(81) * valids
            policy = policy / np.sum(policy)
            P[sTuple] = policy

            Ns[sTuple] = 1

            for a in possibleA:
                Q[(sTuple, a)] = 0
                Nsa[(sTuple, a)] = 0
                W[(sTuple, a)] = 0
            return -v

        best_uct = -100
        for a in possibleA:

            uct_a = Q[(sTuple, a)] + cpuct * P[sTuple][a] * \
                (math.sqrt(Ns[sTuple]) / (1 + Nsa[(sTuple, a)]))

            if uct_a > best_uct:
                best_uct = uct_a
                best_a = a

        next_state, mini_board, wonBoard = move(s, best_a, current_player)

        if wonBoard:
            v = 1
        else:
            current_player *= -1
            v = mcts(next_state, current_player, mini_board)
    else:
        return 0

    W[(sTuple, best_a)] += v
    Ns[sTuple] += 1
    Nsa[(sTuple, best_a)] += 1
    Q[(sTuple, best_a)] = W[(sTuple, best_a)] / Nsa[(sTuple, best_a)]
    return -v


def get_action_probs(init_board, current_player, mini_board):

    for _ in range(mcts_search):
        s = copy.deepcopy(init_board)
        value = mcts(s, current_player, mini_board)

    # print ("done one iteration of MCTS")

    actions_dict = {}

    sArray = board_to_array(init_board, mini_board, current_player)
    sTuple = tuple(map(tuple, sArray))

    for a in possiblePos(init_board, mini_board):
        actions_dict[a] = Nsa[(sTuple, a)] / Ns[sTuple]

    action_probs = np.zeros(81)

    for a in actions_dict:
        np.put(action_probs, a, actions_dict[a], mode='raise')

    return action_probs


def playgame():
    # print("Play game")
    done = False
    current_player = 1
    game_mem = []
    mini_board = 9

    real_board = get_empty_board()
    t = 1
    while not done:
        s = copy.deepcopy(real_board)
        policy = get_action_probs(s, current_player, mini_board)
        policy = policy / np.sum(policy)
        game_mem.append([board_to_array(real_board, mini_board,
                        current_player), current_player, policy, None])
        action = np.random.choice(len(policy), p=policy)

        # print ("policy ", policy)
        print("Turn:", t, "  Chosen action:", action)

        # print ("mini-board", mini_board)
        # print_board(real_board)

        next_state, mini_board, wonBoard = move(
            real_board, action, current_player)

        if len(possiblePos(next_state, mini_board)) == 0:
            for tup in game_mem:
                tup[3] = 0
            return game_mem

        if wonBoard:
            for tup in game_mem:
                if tup[1] == current_player:
                    tup[3] = 1
                else:
                    tup[3] = -1
            return game_mem

        current_player *= -1
        s = next_state
        t += 1


def neural_network():
    # 20 layer residual netowork, policy + value. || 3 CNN + 2 Dense
    # Policy: vector probabilities of certain action
    # Value: [-1,1] estimation current player win from this state
    input_layer = layers.Input(shape=(9, 9), name="BoardInput")
    reshape = layers.core.Reshape((9, 9, 1))(input_layer)
    conv_1 = layers.Conv2D(128, (3, 3), padding='valid',
                           activation='relu', name='conv1')(reshape)
    conv_2 = layers.Conv2D(128, (3, 3), padding='valid',
                           activation='relu', name='conv2')(conv_1)
    conv_3 = layers.Conv2D(128, (3, 3), padding='valid',
                           activation='relu', name='conv3')(conv_2)

    conv_3_flat = layers.Flatten()(conv_3)

    dense_1 = layers.Dense(512, activation='relu', name='dense1')(conv_3_flat)
    dense_2 = layers.Dense(256, activation='relu', name='dense2')(dense_1)

    pi = layers.Dense(81, activation="softmax", name='pi')(dense_2)
    v = layers.Dense(1, activation="tanh", name='value')(dense_2)

    model = Model(inputs=input_layer, outputs=[pi, v])
    model.compile(loss=['categorical_crossentropy',
                  'mean_squared_error'], optimizer=Adam(learning_rate))

    model.summary()
    return model


def train_nn(nn, game_mem):
    print("Training Network")
    print("Length of game_mem", len(game_mem))

    state = []
    policy = []
    value = []

    for mem in game_mem:
        state.append(mem[0])
        policy.append(mem[2])
        value.append(mem[3])

    state = np.array(state)
    policy = np.array(policy)
    value = np.array(value)

    nn.fit(state, [policy, value], batch_size=32,
           epochs=training_epochs, verbose=1)


def pit(nn, new_nn):
    print("Pitting networks")
    nn_wins = 0
    new_nn_wins = 0

    for i in range(n_pit_network):
        print("Game ", i)
        s = []
        mini_board = 9

        for _ in range(9):
            s.append([[" ", " ", " "],
                      [" ", " ", " "],
                      [" ", " ", " "]])

        while True:
            # old nn makes move
            policy, v = nn.predict(board_to_array(
                s, mini_board, 1).reshape(1, 9, 9))
            valids = np.zeros(81)

            possibleA = possiblePos(s, mini_board)

            if len(possibleA) == 0:
                break

            np.put(valids, possibleA, 1)
            policy = policy.reshape(81) * valids
            policy = policy / np.sum(policy)
            action = np.argmax(policy)

            next_state, mini_board, win = move(s, action, 1)
            s = next_state
            if win:
                print("Old NN attack wins")
                nn_wins += 1
                break

            # new nn makes move, second turn
            policy, v = new_nn.predict(board_to_array(
                s, mini_board, -1).reshape(1, 9, 9))
            valids = np.zeros(81)

            possibleA = possiblePos(s, mini_board)

            if len(possibleA) == 0:
                break

            np.put(valids, possibleA, 1)
            policy = policy.reshape(81) * valids
            policy = policy / np.sum(policy)
            action = np.argmax(policy)

            next_state, mini_board, win = move(s, action, -1)
            s = next_state

            if win:
                print("New NN defense wins")
                new_nn_wins += 1
                break

    print("~~~~~~~~~~~~~~")

    if (new_nn_wins + nn_wins) == 0:
        print("All games were complete tie")
        return False

    win_percent = float(new_nn_wins) / float(new_nn_wins + nn_wins)
    print("Result over ", n_pit_network, " matches.")
    print("New NN win: ", new_nn_wins)
    print("Old NN win: ", nn_wins)
    print("Win percent: ", win_percent)

    if win_percent > 0.59:
        print("The new network won")
        # print (win_percent)
        return True
    else:
        print("The new network lost")
        # print (win_percent)
        return False


def get_model_num(path):
    global nn, Q, Nsa, Ns, W, P
    ans = 0
    if not os.path.exists(path):
        os.mkdir(path)
        return ans

    for (_, _, filenames) in walk(path):
        for file in filenames:
            if file.endswith(".h5") and file.startswith("model_") and file != "model_best.h5":
                cnt = int(file.split(".h5")[0].split("model_")[1])
                ans = max(ans, cnt)
        break

    return ans


nn = neural_network()


def train():
    global nn, Q, Nsa, Ns, W, P
    game_mem = []
    num = get_model_num(save_model_path)

    # Load NN model
    if num > 0:
        print("Loading model {} from modes_def folder".format(num))
        filename = 'model_{}.h5'.format(num)
        nn = models.load_model(os.path.join(save_model_path, filename))

    # Load global variables
    if os.path.exists(os.path.join(save_model_path, 'variables.pkl')):
        print("Loading global variables from modes_def folder")
        with open(os.path.join(save_model_path, 'variables.pkl'), 'rb') as f:
            var_dict = pickle.load(f)
            Q = var_dict['Q']
            Nsa = var_dict['Nsa']
            Ns = var_dict['Ns']
            W = var_dict['W']
            P = var_dict['P']
    else:
        print("Loading: Global variables pkl file is empty")
        input_dictionary = {'Q': Q, 'Nsa': Nsa, 'Ns': Ns,
                            'W': W, 'P': P}  # dictionary of tuple
        file = open(os.path.join(save_model_path, 'variables.pkl'), 'wb')
        pickle.dump(input_dictionary, file)
        file.close()

    # Train model in 100 epoch
    for episode in range(train_episodes):
        print("*************** Eposide {} ***************".format(episode))

        # nn.save('temp.h5')
        # old_nn = models.load_model('temp.h5')

        nn.save(os.path.join(save_model_path, 'temp.h5'))
        old_nn = models.load_model(os.path.join(save_model_path, 'temp.h5'))

        for i in range(playgames_before_training):
            print("~~~~~ Play game for setting up MTCS. Game ", i, " ~~~~~")
            game_mem += playgame()

        print("~~~~~ Training model with CNN ~~~~~")
        train_nn(nn, game_mem)  # GPU

        game_mem = []
        print("~~~~~ Test game with old nn | 20 games ~~~~~")
        if pit(old_nn, nn):  # Test game more faster
            # New nn won
            print("Update the new model")
            del old_nn
            Q = {}
            Nsa = {}
            Ns = {}
            W = {}
            P = {}
            num += 1
            filename = 'model_{}.h5'.format(num)
            model_path = os.path.join(save_model_path, filename)
            nn.save(model_path)

            input_dictionary = {'Q': Q, 'Nsa': Nsa, 'Ns': Ns,
                                'W': W, 'P': P}  # dictionary of tuple
            file = open(os.path.join(save_model_path, 'variables.pkl'), 'wb')
            pickle.dump(input_dictionary, file)
            file.close()
        else:
            # New nn lost
            # The model is still unchanged, but the global variables (Q,Nsa, Ns, W,P) conitnue updating
            nn = old_nn
            del old_nn
            print(
                "The model is still unchanged, but the global variables conitnue updating")
            input_dictionary = {'Q': Q, 'Nsa': Nsa, 'Ns': Ns,
                                'W': W, 'P': P}  # dictionary of tuple
            file = open(os.path.join(save_model_path, 'variables.pkl'), 'wb')
            pickle.dump(input_dictionary, file)
            file.close()


train()
