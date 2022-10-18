from shutil import move
from telnetlib import STATUS
from typing import Tuple
from Bot import Bot
from GameAction import GameAction
from GameState import GameState
import numpy as np
import threading
from copy import deepcopy
import random as rnd

ꝏ = 999


class PekoBot(Bot):
    def __init__(self):
        self.depth_threshold = 7
        self.halt_thinking_event = threading.Event()
        self.halt_thinking_thread = threading.Timer(5, self.halt_thinking_event.set)
    #     self.actions = []

    def get_action(self, state: GameState) -> GameAction:
        # print("depth threshold:", self.depth_threshold)
        # self.depth_threshold += 1
        print("New Actions")
        
        return self.minimax(state)
    
    def minimax(self, state: GameState) -> GameAction:
        
        # print("Begin Minimax")
        # print(state.board_status)
        # print("Minimax")
        self.halt_thinking_thread.start()
        
        v, act = self.max_value(state, 0, -ꝏ, ꝏ, False)
        # print("End Minimax")
        # print(state.board_status)
        # print("value:", v)
        # print("action:",act.action_type + "(" + str(act.position[0]) + "," + str(act.position[1]) + ")")
        print(act)
        print(v)
        
        self.reset_timer()
        return act

    def max_value(self, state:GameState, depth, α, β, skip) -> Tuple[int, GameAction]:
        # print("MAX : ", depth)
        if skip:
            return self.min_value(state, depth+1, α, β, False)
        
        if self.terminal_test(state) or depth >= self.depth_threshold:
            return self.utility(state, -1), None
        

        v = -ꝏ
        # act = None
        # print("jumlah aksi:", len(self.action(state)))
        actions = self.action(state)
        # act = actions[0]
        for action in actions:
            # print(action)

            temp = deepcopy(state)

          
            check = deepcopy(state)
            initial_score = len(np.argwhere(state.board_status == -4))
            new_score = len(np.argwhere(self.result(check, action, -1).board_status == -4))
            # print("newscore :", initial_score)
            # print("newscore :", new_score)
        
            if new_score > initial_score:
                # print("skip from max")
                # print("before :", v)
                # if (depth+1 == self.depth_threshold):
                #     v_result = self.utility(self.result(temp, action, -1), -1)
                # else:
                v_result = self.min_value(self.result(temp, action, -1), depth+1, α, β, True)[0]
                
                # print("after :", v)
            else:
                v_result = self.min_value(self.result(temp, action, -1), depth+1, α, β, False)[0]
            # print(v_result)

            if v_result > v:
                v = v_result
                act = action

            if self.halt_thinking_event.is_set():
                koorX = 0
                koorY = 0
                neutralMove = False
                mehMove = False
                goodMove = False
                moveContainer = []
                mehMoveContainer = []
                panjangBoard = len(state.board_status)
                for i in range(panjangBoard):
                    for j in range(len(state.board_status[i])):

                        if(abs(state.board_status[i][j])==0):
                            neutralMove = True
                            koorX = i
                            koorY = j
                            moveContainer.append((i,j))
                        elif(abs(state.board_status[i][j])==1):
                            if(not neutralMove):
                                mehMove = True
                                koorX = i
                                koorY = j
                                mehMoveContainer.append((i,j))
                        elif(abs(state.board_status[i][j])==2):
                            if(not neutralMove and not mehMove):
                                koorX = i
                                koorY = j
                        elif(abs(state.board_status[i][j])==3):
                            goodMove = True
                            koorX = i
                            koorY = j
                            break
                    if(goodMove):
                        break
                if(not goodMove and neutralMove):
                    randNum = rnd.randrange(len(moveContainer))
                    tupRand = moveContainer[randNum]
                    koorX = tupRand[0]
                    koorY = tupRand[1]
                
                if(not goodMove and not neutralMove and mehMove):
                    randNum = rnd.randrange(len(mehMoveContainer))
                    tupRand = mehMoveContainer[randNum]
                    koorX = tupRand[0]
                    koorY = tupRand[1]

                print("MAX koordinat: ", koorY,koorX)
                print(state.board_status)
                print("ROW")
                print(state.row_status)
                print("COL")
                print(state.col_status)
                possActions = []
                if(state.row_status[koorX][koorY] == 0):
                    act = GameAction("row",(koorY,koorX))
                    possActions.append(act)
                if(state.row_status[koorX+1][koorY] == 0):
                    act = GameAction("row",(koorY,koorX+1))
                    possActions.append(act)
                if(state.col_status[koorY][koorX] == 0):
                    act = GameAction("col",(koorX,koorY))
                    possActions.append(act)
                if(state.col_status[koorY][koorX+1] == 0):
                    act = GameAction("col",(koorX+1,koorY))
                    possActions.append(act)

                if(len(possActions)>0):
                    randNum = rnd.randrange(len(possActions))
                    print(randNum)
                    act = possActions[randNum]

                return v, act

            if v >= β:
                # print("pruning")
                return v, act

            α = max(α, v)
        # print("max", depth, "v:", v)
        return v, act

    def min_value(self, state:GameState, depth, α, β, skip) -> Tuple[int, GameAction]:
        # print("MIN : ", depth)
        if skip:
            return self.max_value(state, depth+1, α, β, False)

        if self.terminal_test(state) or depth >= self.depth_threshold:
            # print("depth:", depth)
            return self.utility(state, 1), None


        v = ꝏ
        # act = None
        # print("jumlah aksi:", len(self.action(state)))
        actions = self.action(state)
        # act = actions[0]
        for action in actions:
            # print(action)

            temp = deepcopy(state)

            check = deepcopy(state)
            initial_score = len(np.argwhere(state.board_status == 4))
            new_score = len(np.argwhere(self.result(check, action, 1).board_status == 4))

            if new_score > initial_score:
                # print("skip from min")
                # print("before :", v)
                # if (depth+1 == self.depth_threshold):
                #     v_result = self.utility(self.result(temp, action, 1), 1)
                # else:
                v_result = self.max_value(self.result(temp, action, 1), depth+1, α, β, True)[0]
                
                # print("after :", v)
            else:        
                v_result = self.max_value(self.result(temp, action, 1), depth+1, α, β, False)[0]

            if v_result < v:
                v = v_result
                act = action

            if self.halt_thinking_event.is_set():
                # koorX = 0
                # koorY = 0
                # neutralMove = False
                # goodMove = False
                # moveContainer = []
                # panjangBoard = len(state.board_status)
                # for i in range(panjangBoard):
                #     for j in range(len(state.board_status[i])):
                #         if(abs(state.board_status[i][j])<1):
                #             neutralMove = True
                #             koorX = i
                #             koorY = j
                #             moveContainer.append((i,j))
                #         elif(abs(state.board_status[i][j])<=2):
                #             goodMove = True
                #             koorX = i
                #             koorY = j
                #             break
                #         elif(abs(state.board_status[i][j])<=3):
                #             if(not neutralMove):
                #                 koorX = i
                #                 koorY = j
                            
                #     if(goodMove):
                #         break
                # if(not goodMove and neutralMove):
                #     randNum = rnd.randrange(len(moveContainer))
                #     tupRand = moveContainer[randNum]
                #     koorX = tupRand[0]
                #     koorY = tupRand[1]

                
                # print("MIN koordinat: ", koorX,koorY)
                # print(state.board_status)
                
                # if(state.row_status[koorX][koorY] == 0):
                #     act = GameAction("row",(koorY,koorX))
                # elif(state.row_status[koorX+1][koorY] == 0):
                #     act = GameAction("row",(koorY,koorX+1))
                # elif(state.col_status[koorY][koorX] == 0):
                #     act = GameAction("col",(koorY,koorX))
                # elif(state.col_status[koorY][koorX+1] == 0):
                #     act = GameAction("col",(koorY,koorX+1))
                return v, act

            if v <= α:
                # print("pruning")
                return v, act
            

            β = min(β, v)
        # print("min", depth, "v:", v)
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

        return Actions

    def result(self, state:GameState, action:GameAction, player):
        x, y = action.position[0], action.position[1]
        val = 1
        [mat_ny, mat_nx] = state.board_status.shape
        # print("before")
        # print(state.board_status)
        # print(state.row_status)
        # print(state.col_status)

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
        # print("after")
        # print(state.board_status)
        return state

    def terminal_test(self, state:GameState):
        return np.all(state.row_status == 1) and np.all(state.col_status == 1)

    def utility(self, state: GameState, player):
        player1_score = len(np.argwhere(state.board_status == -4))
        player2_score = len(np.argwhere(state.board_status == 4))
        # for i in range()
        # print(player1_score, player2_score)
        # print("utilitas:", player1_score - player2_score)
        # print("predict", self.predict(state, player))
        # print(self.depth_threshold)
        block3 = len(np.argwhere(abs(state.board_status) == 3))
        block2 = len(np.argwhere(abs(state.board_status) == 2))
        block1 = len(np.argwhere(abs(state.board_status) == 1))

        # predict = -predict if self.depth_threshold else predict
        # print(state.board_status)
        # print("player1_score:", player1_score, "player2_score:", player2_score)
        # print("predict :", predict)
        if block3 > 0:
            point = -666
        else:
            point = (block1 * 0.25) + (block2 * 0.0625)

        return (player1_score - player2_score) + point

    def predict(self, state: GameState, player):
        matrix_board = state.board_status
        matrix_row = state.row_status
        matrix_col = state.col_status   
        
        
        [mat_ny, mat_nx] = matrix_board.shape
        # print(matrix_board)

        # for i in range(mat_nx):
        #     for j in range(mat_ny):
        #         # print(state.board_status)
                
        #         if abs(matrix_board[j][i]) == 3:
        #             print("i:", i, "j:", j)
        #             # temp = deepcopy(state)
        #             # act = None
        #             # print("Tolol")
                    
        #             # if matrix_row[j][i] == 0:
        #             #     act = GameAction("row", (i,j))
        #             # elif matrix_col[j][i] == 0:
        #             #     act = GameAction("col", (i,j))

        #             # if i < mat_nx and j < mat_ny:
        #             #     if matrix_row[j+1][i] == 0:
        #             #         act = GameAction("row", (i,j+1))
        #             #     elif matrix_col[j][i+1] == 0:
        #             #         act = GameAction("col", (i+1,j))
                    
        #             # if i > 0 and j > 0:
        #             #     if matrix_row[j-1][i] == 0:
        #             #         act = GameAction("row", (i,j-1))
        #             #     elif matrix_col[j][i-1] == 0:
        #             #         act = GameAction("col", (i-1,j)) 
        #             # if act is not None:
        #                 # return self.predict(self.result(temp, act, player), player) + 1
        #             return 1
        # return 0
    
    def reset_timer(self):
        self.halt_thinking_event = threading.Event()
        self.halt_thinking_thread = threading.Timer(5, self.halt_thinking_event.set)