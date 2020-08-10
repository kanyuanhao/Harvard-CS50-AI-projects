"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    num_x = 0
    num_o = 0
    for row in board:
        for element in row:
            if element == X:
                num_x += 1
            elif element == O:
                num_o += 1
    if not terminal(board):
        if num_x > num_o:
            return O
        if num_x == num_o:
            return X
    else:
        return None
                


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_moves = set()

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_moves.add((i, j))
    return possible_moves
    


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if terminal(board):
        raise ValueError("Game Over")
    elif action not in actions(board):
        raise ValueError("Invalid Action")
    else:
        player_name = player(board)
        result_board = copy.deepcopy(board)
        (i, j) = action
        result_board[i][j] = player_name
    return result_board

                          
def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(3):

        if (board[i][0] == board[i][1] == board[i][2] and board[i][0] != None):
            return board[i][0]

        elif (board[0][0] == board[1][1] == board[2][2] or (board[0][2] == board[1][1] == board[2][0]) and board[1][1] != None):
             return board[1][1]

        elif (board[0][i] == board[1][i] == board[2][i] and board[0][i] != None):
             return board[1][i]
            
    return None



def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True
    
    for row in board:
        for element in row:
            if element == EMPTY:
                return False
    return True



def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)
    if win == X:
        return 1
    elif win == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    player_name = player(board)

    if terminal(board):
        return None

    elif board == initial_state():
        return (1,1)
    elif player_name == X:
        v = float("-inf")
        selected_action = None
        for action in actions(board):
            minValueResult = minValue(result(board, action))
            if minValueResult > v:
                v = minValueResult
                selected_action = action
    elif player_name == O:
        v = float("inf")
        selected_action = None
        for action in actions(board):
            maxValueResult = maxValue(result(board, action))
            if maxValueResult < v:
                v = maxValueResult
                selected_action = action
    return selected_action


def maxValue(board):
    if terminal(board):
        return utility(board)
    v = float("-inf")
    for action in actions(board):
        v = max(v, minValue(result(board, action)))
    return v

def minValue(board):
    if terminal(board):
        return utility(board)
    v = float("inf")
    for action in actions(board):
        v = min(v, maxValue(result(board, action)))
    return v
