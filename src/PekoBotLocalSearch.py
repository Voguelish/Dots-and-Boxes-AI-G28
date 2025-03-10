from Bot import Bot
from GameAction import GameAction
from GameState import GameState
import multiprocessing as mp
from copy import deepcopy
import numpy as np
class PekoBotLocalSearch(Bot):
    def get_action(self, state: GameState) -> GameAction:
        mgr = mp.Manager()
        rv = mgr.dict()
        timeinst = mp.Process(target=self.thinking, args=(state, rv))
        timeinst.start()
        timeinst.join(5)
        if timeinst.is_alive():
            # Timeout, returning best action so far...
            timeinst.terminate()
            timeinst.join()
        return rv.values()[0]

    def objective(self, state: GameState) -> int:
        total = 0
        if state.player1_turn:
            sign = -1 # acting as player 1
        else:
            sign = 1 # acting as player 2

        for i in state.board_status:
            for j in i:
                nextMoveState = j * sign
                if nextMoveState == 3: # Move creates possibility for opponent to finish a square by their next turn
                    total -= 10 # Objective function greatly reduced
                elif nextMoveState == 4: # Move finishes a square
                    total += 10 # Objective function greatly increased
                elif nextMoveState == 2: # Move doesn't create possibility for opponent to finish a square by their next turn
                    total += 5 # Objective function increased

        return total
    
    def adv_board_status_once(self, state:GameState, act: GameAction) -> GameState:
        logical_position = act.position
        type = act.action_type
        x = logical_position[0]
        y = logical_position[1]
        val = 1
        playerModifier = 1
        number_of_dots = 4
        retGs = deepcopy(state)
        if retGs.player1_turn:
            playerModifier = -1

        if y < (number_of_dots-1) and x < (number_of_dots-1):
            retGs.board_status[y][x] = (abs(retGs.board_status[y][x]) + val) * playerModifier

        if type == 'row':
            retGs.row_status[y][x] = 1
            if y >= 1:
                retGs.board_status[y-1][x] = (abs(retGs.board_status[y-1][x]) + val) * playerModifier

        elif type == 'col':
            retGs.col_status[y][x] = 1
            if x >= 1:
                retGs.board_status[y][x-1] = (abs(retGs.board_status[y][x-1]) + val) * playerModifier
        return retGs

    def thinking(self, state: GameState, retval: GameAction):
        bestObj = -100 # [-10*9 ... 10*9]
        posibGameActions = []
        for y in range(len(state.col_status)):
            for x in range(len(state.col_status[y])):
                if state.col_status[y][x] == 0:
                    posibGameActions.append(GameAction("col", (x, y)))
        for y in range(len(state.row_status)):
            for x in range(len(state.row_status[y])):
                if state.row_status[y][x] == 0:
                    posibGameActions.append(GameAction("row", (x, y)))
        # placeholder
        retval[0] = posibGameActions[0]
        # Get the best action
        for act in posibGameActions:
            new_state = self.adv_board_status_once(state, act)
            new_obj = self.objective(new_state)
            if new_obj >= bestObj:
                retval[0] = act
                bestObj = new_obj
        return