# -*- coding: utf-8 -*-

'''
          _          (`-. 
          \`----.    )  _`)    
   ,__     \__   `\_/  ( `     
    \_\      \__  `|   }    "Fugit irreparabile tempus"    
      \\  .--' \__/    }
       ))/   \__,<  /_/
       ((|  _/_/ `\ \_\_
_________\_____\\  )__\_\___________________________________

'''

import subprocess
import win32api, win32con, win32gui, ImageGrab, re, os, time, sys, Image
import numpy as np
from sklearn_decoder import ImgRecognizer
from random import *
import datetime

#Set here the path to the bot main folder.
sys.path.append('C:\TBB01')

from com.dtmilano.android.viewclient import ViewClient
device, serialno = ViewClient.connectToDeviceOrExit(verbose=False)

#Hardcoded board_box.
l_max = 8
c_max = 6

#The board_box coords are top-left and bottom-left coord points of the grid.
board_box = (55,214,745,1134)
board_size = (6,8)
img_size = (board_box[2]-board_box[0], board_box[3]-board_box[1])
cell_size = (img_size[0]/board_size[0], img_size[1]/board_size[1])
game_board = np.zeros((board_size[1], board_size[0]), dtype=np.int32)
ia_board = []

'''
Hardcoded Grid_Coord:
We use the board coord in order to get the coord of the middle of every cells in the grid,
then we can have a 1 dimension array of 48 cells.

In order to pass from a 2D board to 1D, we use the following formula : row_cell*max_column_nbs+column_cell
To go through the board we'll use coords of type : row*column.
'''
case = []
x = 0
y = 272
for i in range(0, 8):
    for j in range(0, 6):
        case.append((x+114,y))
        x = x + 113
    y = y + 115
    x = 0

random_case = range(0,48)
player_numbers = range(1,5)

recognizer = ImgRecognizer()

'''
We consider three cases here, that will be then used along with the images
recognition on the cells and permits to map the grid with information hat have
more sense than only numbers.
'''
board_dict = {0: 'Empty ', 1: 'Mob ', 2: 'Player '}


'''
This function will print the board using the values just defined below.
'''
def print_board(board):
    for line in board:
        for elem in line:
            print board_dict[elem] + ' ',
        print

'''
We define some functions to have a better 

'''
def Send_Touch(x,y):
    print "Sending Touch at : x/y :" + str(x) + "/" + str(y) 
    device.longTouch(x,y,250)


def Send_Drag(cell_A,cell_B):
    print "Dragging from cells : " + str(cell_A) + " to " + str(cell_B)
    device.drag((cell_A[0], cell_A[1]), (cell_B[0], cell_B[1]), 100, 10)
    time.sleep(1)

def Send_Complex_Drag(final_arg):
    os.system("monkeyrunner C:/TBB01/MonkeyScripts/m_send_complex_drag.py " + final_arg)

def Send_Take_Snapshot():
    device.takeSnapshot().save("Images/snapshot.png", 'PNG')
    time.sleep(1)

def grab_board():
    img = Image.open('C:/TBB01/Images/snapshot.png')
    img = img.crop(board_box)
    #img.save('C:/TBB01/images/snapshot_crop.png')
    for y in range(0, 8):
        for x in range(0, 6):
            cell_box = (x*cell_size[0], y*cell_size[1], (x+1)*cell_size[0], (y+1)*cell_size[1])
            cell = img.crop(cell_box)
            #cell.save('C:/TBB01/Images/Cells/{0}_{1}.png'.format(y, x))
            game_board[y][x] = recognizer.predict(cell)
            ia_board.append(recognizer.predict(cell))
    print_board(game_board)

#Check board at given coord, to see if it's a player.
def Is_player(l,c):
    if game_board[l][c] == 2:
        return True
    else:
        return False

#Check if empty.
def Is_empty(l,c):
    if game_board[l][c] == 0:
        return True
    else:
        return False

#Check if mob.
def Is_mob(l,c):
    if game_board[l][c] == 1:
        return True
    else:
        return False

#Check around the given case, and try a move to unlock situation.
def Unlock_01(l,c):
    A = l*c_max+c
    if Is_empty(l,c-1) and c>0:
        B = l*c_max+c-1
        Final_Send_Complex_Drag((A,B,B,A))
    elif Is_empty(l,c+1) and c<5:
        B = l*c_max+c+1
        Final_Send_Complex_Drag((A,B,B,A))
    elif Is_empty(l-1,c) and l>0:
        B = l*c_max+c-c_max
        Final_Send_Complex_Drag((A,B,B,A))
    elif Is_empty(l+1,c) and l<7:
        B = l*c_max+c+c_max
        Final_Send_Complex_Drag((A,B,B,A))

'''
Check the side of a case of coord (l,c) to see if a clamp is possible.
Sometimes ennemies can be stacked in row or column like : 

# = enemy   => [&,#,#,#,&]
In the example below we have three stacked enemy, and a clamp is still possible,
if the allies are put where i put the & symbols.

Thats why there is the r1,r2,r3,r4 parameters that are used in recursivity. Each time the function
is called with one of those parameter equal to 1, the function know it is  recursivity and it has to check the
next cell.
'''
def Check_Side(l,c, r1,r2,r3,r4):
    print "----------Attack Module-------------"
    print "mob found at ["+str(l)+", "+str(c)+"]"
    print "------------------------------------"
    print "Checking Horizontals Sides."
    if c<5 and c>0:
        if Is_player(l,c+1) or r1 ==1:
            print "player found at ["+str(l)+", "+str(c+1)+"]"
            if Is_empty(l,c-1):
                print "empty found at ["+str(l)+", "+str(c-1)+"]"
                A = Get_Closest_Ally(l,c-1,(l,c+1))
                B = l*c_max+c-1
                Send_Drag(case[A],case[B])
                return(1)
            elif Is_mob(l,c-1):
                print "recurrence step"
                Check_Side(l,c-1, 1,0,0,0)
            elif Is_player(l,c-1):
                Unlock_01(l,c-1)
                return(1)
        elif Is_player(l,c-1) or r2 ==1:
            print "player found at ["+str(l)+", "+str(c-1)+"]"
            if Is_empty(l,c+1):
                print "empty found at ["+str(l)+", "+str(c+1)+"]"
                A = Get_Closest_Ally(l,c+1,(l,c-1))
                B = l*c_max+c+1
                Send_Drag(case[A],case[B])
                return(1)
            elif Is_mob(l,c+1):
                print "recurrence step"
                Check_Side(l,c+1, 0,1,0,0)
            elif Is_player(l,c+1):
                Unlock_01(l,c+1)
                return(1)
    print "------------------------------------"
    print "Checking Verticals Sides."
    print "------------------------------------"
    if l<7 and l>0:
        if Is_player(l+1,c) or r3 ==1:
            print "player found at ["+str(l+1)+", "+str(c)+"]"
            if Is_empty(l-1,c):
                print "empty found at ["+str(l-1)+", "+str(c)+"]"
                A = Get_Closest_Ally(l-1,c,(l+1,c))
                B = (l*c_max)-c_max+c
                Send_Drag(case[A],case[B])
                return(1)
            elif Is_mob(l-1,c):
                print "recurrence step"
                Check_Side(l-1,c, 0,0,1,0)
            elif Is_player(l-1,c):
                Unlock_01(l-1,c)
                return(1)
        elif Is_player(l-1,c) or r4 ==1:
            print "player found at ["+str(l-1)+", "+str(c)+"]"
            if Is_empty(l+1,c):
                print "empty found at ["+str(l+1)+", "+str(c)+"]"
                A = Get_Closest_Ally(l+1,c,(l-1,c))
                B = (l*c_max)+c_max+c
                Send_Drag(case[A],case[B])
                return(1)
            elif Is_mob(l+1,c):
                print "recurrence step"
                Check_Side(l+1,c, 0,0,0,1)
            elif Is_player(l+1,c):
                Unlock_01(l+1,c)
                return(1)
    print "End Checking Sides."
    return(0)

def Get_Closest_Ally(pr_l,pr_c,ignore):
    result = 0
    num = 100
    for l in range(0, 8):
        for c in range(0, 6):
            if Is_player(l,c) and (l,c) != ignore:
                if abs(l-pr_l)+abs(c-pr_c) < num:
                    num = abs(l-pr_l)+abs(c-pr_c)
                    result = l*c_max+c
    print "Getting Closest Ally : " + str(result)
    return(result)

def Start_Sandwich(type, l, c):
    print "Starting Sandwich."
    if type == 0 and c<5 and c>0 and Is_empty(l,c-1) and Is_empty(l,c+1):
        print "Horizontal Sandwich."
        A = Get_Closest_Ally(l,c,100)
        B = l*c_max+c+choice((-1,1))
        Send_Drag(case[A],case[B])
        return(1)
    elif type == 1 and l<7 and l>0 and Is_empty(l-1,c) and Is_empty(l+1,c):
        print "Vertical Sandwich."
        A = Get_Closest_Ally(l,c,100)
        B = l*c_max+c+choice((-c_max,c_max))
        Send_Drag(case[A],case[B])
        return(1)
    return(0)

'''
Look for a score to answer the question : which clamp is the best, vertical or horizontal ?
If 1 is returned it is vertical.
'''
def Get_Score(pr_l,pr_c):
    s_upleft = 0
    s_upright = 0
    s_downleft = 0
    s_downright = 0
    for l in range(0, 8):
        for c in range(0, 6):
            if game_board[l][c] != 0 and game_board[l][c] != -1:
                if c > pr_c and l > pr_l:
                    s_downright = s_downright + 1
                if c < pr_c and l > pr_l:
                    s_downleft = s_downleft + 1
                if c > pr_c and l < pr_l:
                    s_upleft = s_upleft + 1
                if c < pr_c and l < pr_l:
                    s_upright = s_upright + 1
    s_v = abs(((s_upleft/float(6))+(s_upright/float(6)))-((s_downleft/float(6))+(s_downright/float(6))))
    s_h = abs(((s_upleft/float(6))+(s_downleft/float(6)))-((s_upright/float(6))+(s_downright/float(6))))
    print "Score Horizontal : " + "%f" % s_h
    print "Score Vertical : " + "%f" % s_v
    if s_h > s_v:
        return(1)
    else:
        return(0)

def Get_Mob_Board():
    mob_board = []
    for l in range(0, 8):
        for c in range(0, 6):
            if Is_mob(l,c):
                mob_board.append((l,c))
    return(mob_board)

def Play_turn():

    mob_board = Get_Mob_Board()
    for i in range(0,len(mob_board)):
        if Check_Side(mob_board[i][0],mob_board[i][1],0,0,0,0) == 1:
            return
    for i in range(0,len(mob_board)):
        if(Start_Sandwich(Get_Score(mob_board[i][0],mob_board[i][1]),mob_board[i][0],mob_board[i][1])) == 1:
            return
    Move_Randomly()
    return

'''
Move randomly in case the game is blocked.
'''
def Move_Randomly():
    for i in range(0, 8):
        for j in range(0, 6):
            if game_board[i][j] == choice(player_numbers):
                A = i*6+j
                B = choice(random_case)
                Send_Drag(case[A],case[B])


'''
This is a specific drag that is done with monkeyRunner,
it permits to give an array of cells, and the drag will be done
following each cells given in the array.

This permits to do some accurate dragging and start complex movement.
This code is not used in this bot version.
'''

#Return tab of arguments to parse.
def Create_Special_Argument(t_nb):
    cs_board = []
    cs_01 = "case["
    cs_02 = "]"
    for i in range(0, len(t_nb)):
        cs_board.append(cs_01+str(t_nb[i])+cs_02)	
    return cs_board

#Return the final argument parsed.
def Parse_Special_Argument(cs_board):
    final_arg = ""
    for i in range(0, len(cs_board)):
        if i==len(cs_board)-1:
            final_arg = final_arg+(cs_board[i])
        else:
            final_arg = final_arg+(cs_board[i]+",")
    return final_arg

#Return the complete function with arguments in a string.
def Parse_Final_Argument(final_arg):
    scd = "ext.complex_drag_executor(("
    scd = scd + final_arg + ",444),device)"
    return scd

def Final_Send_Complex_Drag(t_nb):
    Send_Complex_Drag(Parse_Final_Argument(Parse_Special_Argument(Create_Special_Argument(t_nb))))


'''
Starting the bot here.	

recognizer will train on the image we've put on training.
'''
recognizer.train()

while(1):
    print "Taking Snapshot"
    Send_Take_Snapshot()
    print "Grabbing Board"
    grab_board()
    print "Playing Turn"
    Play_turn()
    #Feel free to modify the timer here, or to implement end of turn detection.
    time.sleep(10)



