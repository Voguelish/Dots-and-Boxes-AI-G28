from typing import Tuple
from Bot import Bot
from GameAction import GameAction
from GameState import GameState
import numpy as np
import threading
import random
import random as rnd

ꝏ = 999999999999


class PekoBotMinimax(Bot):
    def __init__(self):
        self.state_action = {}
        self.depth_threshold = 5
        self.halt_thinking_event = threading.Event()
        self.halt_thinking_thread = threading.Timer(5, self.halt_thinking_event.set)

    def get_action(self, state: GameState) -> GameAction:
        if np.all(state.board_status == 0) or (len(np.argwhere(abs(state.board_status) == 1)) == 1):
            self.depth_threshold = 5
        return self.minimax(state)
    
    def minimax(self, state: GameState) -> GameAction:
        self.halt_thinking_thread.start()
        box_bot = len(np.argwhere(state.board_status == -4))
        act = self.max_value(state, 0, -ꝏ, ꝏ)[1]

        if len(self.state_action) > 0:
            n = 0
            for action, state in self.state_action.items():
                n += 1
                if len(np.argwhere(abs(state.board_status) == 3)) == 0:
                    act = action
                    break
                
                if len(np.argwhere(state.board_status == -4)) - box_bot > 0:
                    act = action
                    break
                if n == len(self.state_action):
                    act = random.choice(list(self.state_action))
        self.reset_timer()

        return act

    def max_value(self, state:GameState, depth, α, β) -> Tuple[int, GameAction]:      
        if self.terminal_test(state) or depth == int(self.depth_threshold):
            return self.utility(state), None

        v = -ꝏ
        actions = self.action(state)
        i = 0
        for action in actions:

            temp = self.copy_state(state)
            box_before = len(np.argwhere(temp.board_status == -4))
            act_result = self.result(temp, action, -1)
            box_after = len(np.argwhere(act_result.board_status == -4))
            if box_after > box_before:
                v_result = self.max_value(act_result, depth+1, α, β)[0]
            else:
                v_result = self.min_value(act_result, depth+1, α, β)[0]

            if v_result > v:
                v = v_result
                act = action
                if depth == 0:
                    self.state_action = {}

            if v_result == v and depth == 0:
                self.state_action[action] = act_result

            if self.halt_thinking_event.is_set():
                return v, act

            if v >= β:
                return v, act

            α = max(α, v)
            i += 1
        return v, act

    def min_value(self, state:GameState, depth, α, β) -> Tuple[int, GameAction]:
        if self.terminal_test(state) or depth == int(self.depth_threshold):
            return self.utility(state), None
        v = ꝏ

        actions = self.action(state)
        for action in actions:
            temp = self.copy_state(state)
            box_before = len(np.argwhere(temp.board_status == 4))
            act_result = self.result(temp, action, -1)   
            box_after = len(np.argwhere(act_result.board_status == 4))
            if box_after > box_before:
                v_result = self.min_value(act_result, depth+1, α, β)[0]
            else:
                v_result = self.max_value(act_result, depth+1, α, β)[0]
            if v_result < v:
                v = v_result
                act = action

            if self.halt_thinking_event.is_set():
                return v, act

            if v <= α:
                return v, act
            β = min(β, v)
        return v, act

    def action(self, state:GameState):
        matrix_row = state.row_status
        matrix_col = state.col_status

        [row_ny, row_nx] = matrix_row.shape
        [col_ny, col_nx] = matrix_col.shape

        Actions = []

        for i in range(row_nx):
            for j in range(row_ny):
                if matrix_row[j,i] == 0:
                    Actions.append(GameAction("row", (i,j)))

        for i in range(col_nx):
            for j in range(col_ny):
                if matrix_col[j,i] == 0:
                    Actions.append(GameAction("col", (i,j)))
        random.shuffle(Actions)
        return Actions

    def result(self, state:GameState, action:GameAction, player):
        x, y = action.position[0], action.position[1]
        val = 1
        [mat_ny, mat_nx] = state.board_status.shape


        if y < mat_ny and x < mat_nx:
            state.board_status[y][x] = (abs(state.board_status[y][x]) + val) * player
            if state.board_status[y][x] == 4:
                state.board_status[y][x] = (abs(state.board_status[y-1][x]) + val) * player

        if action.action_type == "row":
            state.row_status[y][x] = 1
            if (y >= 1):
                state.board_status[y-1][x] = (abs(state.board_status[y-1][x]) + val) * player
        else:
            if (x >= 1):
                state.board_status[y][x-1] = (abs(state.board_status[y][x-1]) + val) * player
            state.col_status[y][x] = 1
        return state

    def terminal_test(self, state:GameState):
        return np.all(state.row_status == 1) and np.all(state.col_status == 1)

    def utility(self, state: GameState):
        player1_score = len(np.argwhere(state.board_status == -4))
        player2_score = len(np.argwhere(state.board_status == 4))

        block3 = len(np.argwhere(abs(state.board_status) == 3))
        block2 = len(np.argwhere(abs(state.board_status) == 2))

        if block2 + block3 > 5:
            if self.chain(state):
                return player1_score - player2_score - 4

        return player1_score - player2_score

    def chain(self, state: GameState):
        [nx, ny] = state.board_status.shape

        for i in range(nx):
            for j in range(ny):
                if abs(state.board_status[j][i]) == 3:
                    if i == 0 and j == 0:
                        if abs(state.board_status[j][i+1]) == 3 or abs(state.board_status[j+1][i]) == 3:
                            return True
                    elif i < nx and j != ny-1:
                        if abs(state.board_status[j+1][i]) == 3 or abs(state.board_status[j-1][i]) == -3 or abs(state.board_status[j][i-1]) == -3:
                            return True
                    elif j < ny and i != nx-1:
                        if abs(state.board_status[j][i+1]) == 3 or abs(state.board_status[j-1][i]) == -3 or abs(state.board_status[j][i-1]) == -3:
                            return True
                    else:
                        if state.board_status[j][i-1] == 3 or state.board_status[j-1][i] == -3:
                            return True
    
    def copy_state(self, state: GameState) -> GameState:
        return GameState(state.board_status.copy(), 
                             state.row_status.copy(), 
                             state.col_status.copy(), 
                             state.player1_turn)

    def reset_timer(self):
        self.halt_thinking_event = threading.Event()
        self.halt_thinking_thread = threading.Timer(5, self.halt_thinking_event.set)