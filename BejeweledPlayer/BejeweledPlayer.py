# BejeweledPlayer.py
# Created by Poondaedalin
# Not my finest work, but it does automatically play the Steam release version of Bejeweled Deluxe (2001).
# Hold ALT to prematurely stop the program.

# Known issues:
# The code sometimes crashes when trying to get a new move on the random setting.
# The board reader often gets confused when on the speedy setting.
# The board simulation at the bottom of get_children is very buggy, and is unused in the current implementation.

import copy
import time
import pyautogui
import keyboard
import math
import colorsys
import random
from win32gui import FindWindow, GetWindowRect

pyautogui.useImageNotFoundException()

# Enum Key:
# Character 1 - Num 1 [1,2]
# Character 2 - Num 2 [1,2]
# Character 3/4 - Type [Flat (f), Crooked Tail-Down (cd), Crooked Tail-Up (cu), Wedge (v)]
# Character 4/5 - Direction [Horizontal (x), Vertical (y)]

# Modifiers
# first: Always selects the first move (closest to top-left)
# last: Always selects the last move (closest to bottom-right) 
# speedy: Prioritizes horizontal moves over vertical moves
# stickler: Prioritizes vertical moves over horizontal moves

modifiers = ["first","speedy"]
#modifiers = []

move_delay = 0.75
calc_delay = 0.1

if modifiers.count("speedy") > 0:
     move_delay = 0.6
elif modifiers.count("stickler") > 0:
     move_delay = 0.85

class Option():

     def __init__(self, type, pos, color):
          self.type = type
          self.pos = pos
          self.color = color

     def __str__(self):
          return "[" + str(self.type) + ", " + str(self.pos) + ", " + str(self.color) + "]"

def rotate90(A):
    N = len(A[0])
    for i in range(N // 2):
        for j in range(i, N - i - 1):
            temp = A[i][j]
            A[i][j] = A[N - 1 - j][i]
            A[N - 1 - j][i] = A[N - 1 - i][N - 1 - j]
            A[N - 1 - i][N - 1 - j] = A[j][N - 1 - i]
            A[j][N - 1 - i] = temp

def bubble_up(B):
     canBubble = False
     for y in range(len(B)-1,0,-1):
          for x in range(len(B[y])):
               if str.lower(B[y][x]) == 'x' and str.lower(B[y-1][x]) != 'x':
                    (B[y][x],B[y-1][x]) = (B[y-1][x],B[y][x])
                    canBubble = True
     return canBubble

def scan_board():
     
     bj_window = GetWindowRect(FindWindow(None, "Bejeweled Deluxe 1.87"))

     jewel_logo = list(pyautogui.locateAllOnScreen('jeweled.png', confidence=0.6, grayscale=False, region=bj_window))

     starting_pos = (jewel_logo[0].left + jewel_logo[0].width//2 + 128, jewel_logo[0].top + jewel_logo[0].height//2)

     board = [
          [0,0,0,0,0,0,0,0],
          [0,0,0,0,0,0,0,0],
          [0,0,0,0,0,0,0,0],
          [0,0,0,0,0,0,0,0],
          [0,0,0,0,0,0,0,0],
          [0,0,0,0,0,0,0,0],
          [0,0,0,0,0,0,0,0],
          [0,0,0,0,0,0,0,0]]


     s_shot = pyautogui.screenshot()

     for i in range(0,8):
          for j in range(0,8):
               #time.sleep(0.02)

               coords = starting_pos + (i*64,j*64)

               #pyautogui.moveTo((starting_pos[0] + i*64, starting_pos[1] + j*64))

               #print((starting_pos[0] + i*64, starting_pos[1] + j*64))

               hue_matrix = []

               sum = 0

               for n in range(-2,2):
                    for m in range(-2,2):
                         curr_color = s_shot.getpixel((starting_pos[0] + i*64 + m, starting_pos[1] + j*64 + n))
                         hue = colorsys.rgb_to_hsv(curr_color[0], curr_color[1],curr_color[2])[0]*360
                         hue_matrix.append(hue)
               for h in hue_matrix:
                    sum = sum + h

               sum = sum / len(hue_matrix)

               if abs(22 - sum) < 3:
                    board[j][i] = 'o'
               elif abs(60 - sum) < 5:
                    board[j][i] = 'y'
               elif abs(111 - sum) < 3:
                    board[j][i] = 'g'
               elif abs(200 - sum) < 3:
                    board[j][i] = 'b'
               elif abs(300 - sum) < 3:
                    board[j][i] = 'p'
               elif abs(sum) < 3 or abs(360 - sum) < 3:
                    board[j][i] = 'w'
               else:
                    board[j][i] = 'r'

               #board[j][i] = sum
     return board

def make_move(move):
     bj_window = GetWindowRect(FindWindow(None, "Bejeweled Deluxe 1.87"))

     jewel_logo = list(pyautogui.locateAllOnScreen('jeweled.png', confidence=0.6, grayscale=False, region=bj_window))

     starting_pos = (jewel_logo[0].left + jewel_logo[0].width//2 + 128, jewel_logo[0].top + jewel_logo[0].height//2)

     start_coords = (starting_pos[0] + move[2]*64, starting_pos[1] + move[1]*64)
     end_coords = (starting_pos[0] + move[4]*64, starting_pos[1] + move[3]*64)

     pyautogui.click(starting_pos[0] - 50, starting_pos[1])
     pyautogui.moveTo(start_coords[0], start_coords[1])
     time.sleep(calc_delay)
     pyautogui.dragTo(end_coords[0], end_coords[1], 0.1, button='left')



def get_children(B):
     
     options = []

     verbose = False

     for y in range(len(B)):
          for x in range(len(B[y])):

               # The coordinate is the gem that must be moved to match 3, not the origin of the search!

               if x < len(B[y]) - 3 and B[y][x] != 'x' and B[y][x] == B[y][x+1] and B[y][x+1] == B[y][x+3]:
                    options.append(Option("21fx", (y, x+3), B[y][x+3]))

                    if verbose:
                         print("21fx",(y,x), B[y][x], (y,x+1), B[y][x+1], (y,x+3),B[y][x+3])

               elif x < len(B[y]) - 3 and B[y][x] != 'x' and B[y][x] == B[y][x+2] and B[y][x+2] == B[y][x+3]:
                    options.append(Option("12fx", (y, x), B[y][x]))

                    if verbose:
                         print("12fx",(y,x), B[y][x], (y,x+2), B[y][x+2], (y,x+3),B[y][x+3])

               elif y < len(B[y]) - 3 and B[y][x] != 'x' and B[y][x] == B[y+1][x] and B[y+1][x] == B[y+3][x]:
                    options.append(Option("21fy", (y+3, x), B[y+3][x]))

                    if verbose:
                         print("21fy",(y,x), B[y][x], (y+1,x), B[y+1][x], (y+3,x),B[y+3][x])

               elif y < len(B[y]) - 3 and B[y][x] != 'x' and B[y][x] == B[y+2][x] and B[y+2][x] == B[y+3][x]:
                    options.append(Option("12fy", (y, x), B[y][x]))

                    if verbose:
                         print("12fy",(y,x), B[y][x], (y+2,x), B[y+2][x], (y+3,x),B[y+3][x])

               elif (x < len(B[y]) - 2 and y < len(B[y]) - 1) and B[y][x] != 'x' and B[y][x] == B[y+1][x+1] and B[y+1][x+1] == B[y][x+2]:
                    options.append(Option("21vx", (y+1, x+1), B[y+1][x+1]))

                    if verbose:
                         print("21vx",(y,x), B[y][x], (y+1,x+1), B[y+1][x+1], (y,x+2),B[y][x+2])

               elif (x < len(B[y]) - 2 and y > 0) and B[y][x] != 'x' and B[y][x] == B[y-1][x+1] and B[y-1][x+1] == B[y][x+2]:
                    options.append(Option("12vx", (y-1, x+1), B[y-1][x+1]))

                    if verbose:
                         print("12vx",(y,x), B[y][x], (y-1,x+1), B[y-1][x+1], (y,x+2),B[y][x+2])

               elif (x < len(B[y]) - 1 and y < len(B[y]) - 2) and B[y][x] != 'x' and B[y][x] == B[y+1][x+1] and B[y+1][x+1] == B[y+2][x]:
                    options.append(Option("21vy", (y+1, x+1), B[y+1][x+1]))

                    if verbose:
                         print("21vy",(y,x), B[y][x], (y+1,x+1), B[y+1][x+1], (y+2,x),B[y+2][x])

               elif (x > 0 and y < len(B[y]) - 2) and B[y][x] != 'x' and B[y][x] == B[y+1][x-1] and B[y+1][x-1] == B[y+2][x]:
                    options.append(Option("12vy", (y+1, x-1), B[y+1][x-1]))

                    if verbose:
                         print("12vy",(y,x), B[y][x], (y+1,x-1), B[y+1][x-1], (y+2,x),B[y+2][x])

               elif (x < len(B[y]) - 2 and y > 0) and B[y][x] != 'x' and B[y][x] == B[y][x+1] and B[y][x+1] == B[y-1][x+2]:
                    options.append(Option("21cdx", (y-1, x+2), B[y-1][x+2]))
                    
                    if verbose:
                         print("21cdx",(y,x), B[y][x], (y,x+1), B[y][x+1], (y-1,x+2),B[y-1][x+2])

               elif (x < len(B[y]) - 2 and y > 0) and B[y][x] != 'x' and B[y][x] == B[y-1][x+1] and B[y-1][x+1] == B[y-1][x+2]:
                    options.append(Option("12cux", (y, x), B[y][x]))
                    
                    if verbose:
                         print("12cux",(y,x), B[y][x], (y-1,x+1), B[y-1][x+1], (y-1,x+2),B[y-1][x+2])

               elif (x < len(B[y]) - 2 and y < len(B[y]) - 1) and B[y][x] != 'x' and B[y][x] == B[y][x+1] and B[y][x+1] == B[y+1][x+2]:
                    options.append(Option("21cux", (y+1, x+2), B[y+1][x+2]))
                    
                    if verbose:
                         print("21cux",(y,x), B[y][x], (y,x+1), B[y][x+1], (y+1,x+2),B[y+1][x+2])

               elif (x < len(B[y]) - 2 and y < len(B[y]) - 1) and B[y][x] != 'x' and B[y][x] == B[y+1][x+1] and B[y+1][x+1] == B[y+1][x+2]:
                    options.append(Option("12cdx", (y, x), B[y][x]))
                    
                    if verbose:
                         print("12cdx",(y,x), B[y][x], (y+1,x+1), B[y+1][x+1], (y+1,x+2),B[y+1][x+2])

               elif (x < len(B[y]) - 1 and y < len(B[y]) - 2) and B[y][x] != 'x' and B[y][x] == B[y+1][x+1] and B[y+1][x+1] == B[y+2][x+1]:
                    options.append(Option("12Ry", (y, x), B[y][x]))

                    if verbose:
                         print("12Ry",(y,x), B[y][x], (y+1,x+1), B[y+1][x+1], (y+2,x+1),B[y+2][x+1])

               elif (x < len(B[y]) - 1 and y < len(B[y]) - 2) and B[y][x] != 'x' and B[y][x] == B[y+1][x] and B[y+1][x] == B[y+2][x+1]:
                    options.append(Option("21Ly", (y+2, x+1), B[y+2][x+1]))

                    if verbose:
                         print("21Ly",(y,x), B[y][x], (y+1,x), B[y+1][x], (y+2,x+1),B[y+2][x+1])

               elif (x > 0 and y < len(B[y]) - 2) and B[y][x] != 'x' and B[y][x] == B[y+1][x-1] and B[y+1][x-1] == B[y+2][x-1]:
                    options.append(Option("12Ly", (y, x), B[y][x]))

                    if verbose:
                         print("12Ly",(y,x), B[y][x], (y+1,x-1), B[y+1][x-1], (y+2,x-1),B[y+2][x-1])

               elif (x > 0 and y < len(B[y]) - 2) and B[y][x] != 'x' and B[y][x] == B[y+1][x] and B[y+1][x] == B[y+2][x-1]:
                    options.append(Option("21Ry", (y+2, x-1), B[y+2][x-1]))

                    if verbose:
                         print("21Ry",(y,x), B[y][x], (y+1,x-1), B[y+1][x-1], (y+2,x-1),B[y+2][x-1])

     boards = []
     moves = []

     for option in options:

          temp = copy.deepcopy(B)
          oy = option.pos[0]
          ox = option.pos[1]

          if option.type == "21fx":
               (temp[oy][ox],temp[oy][ox-1]) = (temp[oy][ox-1],temp[oy][ox])

               moves.append(["21fx",oy,ox,oy,ox-1])
               boards.append(temp)
          
          elif option.type == "12fx":
               (temp[oy][ox],temp[oy][ox+1]) = (temp[oy][ox+1],temp[oy][ox])

               moves.append(["12fx",oy,ox,oy,ox+1])
               boards.append(temp)

          elif option.type == "21fy":
               (temp[oy][ox],temp[oy-1][ox]) = (temp[oy-1][ox],temp[oy][ox])

               moves.append(["21fy",oy,ox,oy-1,ox])
               boards.append(temp)

          elif option.type == "12fy":
               (temp[oy][ox],temp[oy+1][ox]) = (temp[oy+1][ox],temp[oy][ox])

               moves.append(["12fy",oy,ox,oy+1,ox])
               boards.append(temp)

          elif option.type == "21vx":
               (temp[oy][ox],temp[oy-1][ox]) = (temp[oy-1][ox],temp[oy][ox])

               moves.append(["21vx",oy,ox,oy-1,ox])
               boards.append(temp)

          elif option.type == "12vx":
               (temp[oy][ox],temp[oy+1][ox]) = (temp[oy+1][ox],temp[oy][ox])

               moves.append(["12vx",oy,ox,oy+1,ox])
               boards.append(temp)

          elif option.type == "21vy":
               (temp[oy][ox],temp[oy][ox-1]) = (temp[oy][ox-1],temp[oy][ox])

               moves.append(["21vy",oy,ox,oy,ox-1])
               boards.append(temp)

          elif option.type == "12vy":
               (temp[oy][ox],temp[oy][ox+1]) = (temp[oy][ox+1],temp[oy][ox])
               

               moves.append(["12vy",oy,ox,oy,ox+1])
               boards.append(temp)

          elif option.type == "21cdx":
               (temp[oy][ox],temp[oy+1][ox]) = (temp[oy+1][ox],temp[oy][ox])

               
               moves.append(["21cdx",oy,ox,oy+1,ox])
               boards.append(temp)
               pass

          elif option.type == "12cdx":
               (temp[oy][ox],temp[oy+1][ox]) = (temp[oy+1][ox],temp[oy][ox])

               
               moves.append(["12cdx",oy,ox,oy+1,ox])
               boards.append(temp)
               pass

          elif option.type == "21cux":
               (temp[oy][ox],temp[oy-1][ox]) = (temp[oy-1][ox],temp[oy][ox])

               
               moves.append(["21cux",oy,ox,oy-1,ox])
               boards.append(temp)
               pass

          elif option.type == "12cux":
               (temp[oy][ox],temp[oy-1][ox]) = (temp[oy-1][ox],temp[oy][ox])

               
               moves.append(["12cux",oy,ox,oy-1,ox])
               boards.append(temp)
               pass

          elif option.type == "12Ry":
               (temp[oy][ox],temp[oy][ox+1]) = (temp[oy][ox+1],temp[oy][ox])
               
               moves.append(["12Ry",oy,ox,oy,ox+1])
               boards.append(temp)
               pass

          elif option.type == "21Ly":
               (temp[oy][ox],temp[oy][ox-1]) = (temp[oy][ox-1],temp[oy][ox])
               
               moves.append(["21Ly",oy,ox,oy,ox-1])
               boards.append(temp)
               pass

          elif option.type == "12Ly":
               (temp[oy][ox],temp[oy][ox-1]) = (temp[oy][ox-1],temp[oy][ox])
               
               moves.append(["12Ly",oy,ox,oy,ox-1])
               boards.append(temp)
               pass

          elif option.type == "21Ry":
               (temp[oy][ox],temp[oy][ox+1]) = (temp[oy][ox+1],temp[oy][ox])
               
               moves.append(["21Ry",oy,ox,oy,ox+1])
               boards.append(temp)
               pass


     buffer = []

     for board in boards:

          temp = copy.deepcopy(board)

          canBubble = True

          while canBubble:

               for y in range(len(board)):
                    prev = ''
                    count = 1
                    for x in range(len(board[y])):
                         if board[y][x] == prev:
                              count = count + 1
                         elif count >= 3:
                              for n in range(count):
                                   buffer.append([y,x-n-1,'X'])
                              count = 1
                         else:
                              count = 1
                         prev = board[y][x]

               rotate90(board)

               for y in range(len(board)):
                    prev = ''
                    count = 1
                    for x in range(len(board[y])):
                         if board[y][x] == prev:
                              count = count + 1
                         elif count >= 3:
                              for n in range(count):
                                   board[y][x-n-1] = 'X'
                              count = 1
                         else:
                              count = 1
                         prev = board[y][x]

               rotate90(board)
               rotate90(board)
               rotate90(board)

               for buf in buffer:
                    board[buf[0]][buf[1]] = buf[2]

               buffer = []

               canBubble = bubble_up(board)

          board = temp

     return [boards, moves]

initial_board = []

while initial_board == []:

     time.sleep(0.33)

     try:
          initial_board = scan_board()
     except:
          print("no board found!")
     

children = get_children(initial_board)

index = 0
shift = 0
prev_len = 0

if modifiers.count("last") > 0:
     index = len(children)-1

while (len(children) != 0 and not keyboard.is_pressed('alt')):

     if modifiers.count("first") > 0 and len(children) != 0:
          index = 0
     elif modifiers.count("last") > 0 and len(children) != 0:
          index = len(children[1])-1
     elif len(children) != 0:
          index = random.randrange(0,len(children[1]))
     else:
          index = 0
     #make_move(children[1][random.randrange(0,len(children[1])-1)])

     if (len(children[1]) < 25 and len(children[1]) > 0):
          print(str(len(children[1])) + " -> " + str(index)  + " : " + str(children[1][index]))
          make_move(children[1][index])
     time.sleep(move_delay)
     try:
          initial_board = scan_board()
     except:
          print("no board found!")
     children = get_children(initial_board)
     
     if modifiers.count("first") > 0 and len(children[0]) != 0:
          index = 0
          for i in range(len(children[1])-1):
               child = children[1][i]
               if (child[0][len(child[0])-1] == "x" and modifiers.count("speedy") > 0) or (child[0][len(child[0])-1] == "y" and modifiers.count("stickler") > 0):
                    index = i
                    break
               pass
          pass

     elif modifiers.count("last") > 0 and len(children[0]) != 0:
          index = len(children[1])-1
          for i in range(len(children[1])-1,0,-1):
               child = children[1][i]
               if (child[0][len(child[0])-1] == "x" and modifiers.count("speedy") > 0) or (child[0][len(child[0])-1] == "y" and modifiers.count("stickler") > 0):
                    index = i
                    break
               pass
          pass

     if len(modifiers) == 0:
          if len(children[1])-1 <= 0:
               index = 0
          else:
               index = random.randint(0,len(children[1])-1)

     if len(children[1]) == prev_len:
          shift = shift + 1
          index = (index + shift) % len(children[1])
     else:
          shift = 0
     
     prev_len = children[1]

     #print(children[1][0], len(children[1]))

#print(len(children))