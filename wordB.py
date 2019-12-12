'''
Based on WordBubbles: 
Given an R x C board of characters, find K words, each word
of length k_i in board such that each character is next to the next
character in one of the eight directions, with no reuse of a character
and the entire board is used.

R = # rows in board
C = # cols in board
K = # words to find
W = # words in english dictionary given
S = total sum of lengths of all words in english dictionary

Input:
First line: 3 integers: R, C, K
Second line: K integers, representing the length k_i for each i.

Output:
K different words, with the ith word having length k_i\

Ideas:
- Get lots of common English words into a txt file ("wordBwords.txt")
- Prune #1: Create a set. For every pair of adjacent letters in the board (adjacent = any in the 8 directions),
    add to set.
    - Then for every word in wordBwords.txt, make sure 
        (a) it is of the right length and
        (b) every consecutive pair of letters in word is in the set
    - is a significant reduction from the initial large amounts of words

- Prune #2: Given the words that pass the test above, check the board to see that the word actually exists

- Partition all words that pass the above test into the corresponding lengths, and do a recursive method to find
    all tuples of words such that the sum of the letters in the tuples equals the sum of the letters in board
    - sort initially by longest length first, reduces number of recursive calls drastically (in one example, went from 212,693 recursive calls to 39 calls; another 3120 -> 83; another 9558 -> 109)
    - then lexiographically; take advantage of symmetry (Avoid [["FUN", "WORD"], ["WORD", "FUN"]])
    - sample size isn't that big; reduces possible set of tuples a lot

- Lastly, have to do massive recursion to check that each letter in board is used exactly once.
'''

import math
import timeit

recurseCalls = 0
recurseCalls2 = 0

# all 8 directions
dx = [-1, -1, -1, 0, 1, 1,  1,  0]
dy = [-1,  0,  1, 1, 1, 0, -1, -1]

def printb(arr):
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            if arr[i][j]:
                print("1", end="")
            else:
                print("0", end="")
        print("")
    print("")

def printi(arr):
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            print(arr[i][j], end="")
        print("")
    print("")

# O(1)
# if x and y fall inside the board
def inBounds(R, C, x, y):
    return not (x < 0 or x >= R or y < 0 or y >= C)

# recursive backtracking to determine if str can be found in board
def helper1(R, C, board, visited, x, y, str, index):
    # if found all letters, then return true
    if index == len(str):
        return True

    # traverse in a new direction
    for i in range(8):
        x1 = x + dx[i]
        y1 = y + dy[i]
        # if new direction is valid and is equal to the next letter, recurse
        if inBounds(R, C, x1, y1) and not visited[x1][y1] and board[x1][y1] == str[index]:
            visited[x1][y1] = True
            temp = helper1(R, C, board, visited, x1, y1, str, index + 1)
            visited[x1][y1] = False
            if temp:
                return True
    
# O(RC)
# determines if str can be found in board
def inBoard(R, C, board, str):
    visited = []
    for i in range(R):
        temp = []
        for j in range(C):
            temp.append(False)
        visited.append(temp)

    # finds the position of the first letter before recursing on helper method
    for i in range(R):
        for j in range(C):
            if board[i][j] == str[0]:
                visited[i][j] = True
                temp = helper1(R, C, board, visited, i, j, str, 1)
                visited[i][j] = False
                if temp:
                    return True

    return False

# O(RC * len(words))
# return a new list of words that can actually be found in board
def prune1(R, C, board, words):
    print("prune1")
    valid_words = []
    for word in words:
        if inBoard(R, C, board, word):
            valid_words.append(word)
    
    return valid_words

# O(RC + S)
# read from file, take only those that have the required length
# and where each consecutive pair of letters in each word 
# (a "connection") can be found in board
def prune0(R, C, file_name, lens_set, board):
    connections = set()

    # add all connections; cheap to do (min(RC*RC, 26*25))
    for i in range(R):
        for j in range(C):
            for k in range(8):
                i1 = i + dx[k]
                j1 = j + dy[k]
                if inBounds(R, C, i1, j1):
                    connections.add(board[i][j] + board[i1][j1])

    valid_words = []
    
    # open file
    with open(file_name, "r") as f:
        for line in f.readlines():
            # get rid of \n at each line
            line = line.rstrip("\n")

            # take words only if has correct length
            if(len(line) not in lens_set):
                continue

            # turn upper case
            word = line.upper()
            valid = True
            # check every consecutive pair of letters
            for i in range(len(word) - 1):
                temp = word[i:i+2]
                if temp not in connections:
                    valid = False
                    break
            if valid:
                valid_words.append(word)

    return valid_words

def recurseAll(board, count, lens_map, lens_list, index, temp, result):
    global recurseCalls
    recurseCalls += 1
    
    # if reached this point, we are done
    if(index == len(lens_list)):
        temp2 = []

        # make a copy
        for i in temp:
            temp2.append(i)

        # add to final result
        result.append(temp2)
        return
    
    
    #print("temp =", temp)
    # avoid permutations of words by getting the index of last one, and starting from there rather than from 0
    word_arr = lens_list[index]
    last_arr = lens_map[len(word_arr[0])]
    # for each remaining word,
    for i in range(last_arr[-1] + 1, len(word_arr)):
        word = word_arr[i]

        # update the last index of this length
        last_arr.append(i)

        # subtract letters from count, while still valid
        valid = True
        for j in word:
            count[ord(j) - 65] -= 1
        for j in word:
            if count[ord(j) - 65] < 0:
                valid = False
                break

        # if good to go, recurse further
        if valid:
            temp.append(word)
            recurseAll(board, count, lens_map, lens_list, index + 1, temp, result)
            temp.pop()
        
        # add back count to get more later
        for j in word:
            count[ord(j) - 65] += 1

        # de-update the last index of this length
        last_arr.pop()

    return

def helper2(R, C, board, visited, x, y, str, index, color):
    global recurseCalls2
    recurseCalls2 += 1

    # if found all letters, then return true
    if index == len(str):
        yield True
        return True

    # traverse in a new direction
    for i in range(8):
        x1 = x + dx[i]
        y1 = y + dy[i]

    #    print("str , index =", str, index)
        # if new direction is valid and is equal to the next letter, recurse
        if inBounds(R, C, x1, y1) and visited[x1][y1] == 0 and board[x1][y1] == str[index]:
            visited[x1][y1] = color
            for temp in helper2(R, C, board, visited, x1, y1, str, index + 1, color):
                if temp:
                    yield True
            visited[x1][y1] = 0

    

def check_all_words_fit(board, words, visited, index):
    '''
    print("index = ", index)
    if index == len(words):
        print("at end")
    else:
        print(" before word ", words[index])
    printb(visited)
    '''

    if index == len(words):
        return True

    my_str = words[index]

    R = len(board)
    C = len(board[0])

    for i in range(R):
        for j in range(C):
            if board[i][j] == my_str[0] and visited[i][j] == 0:
                visited[i][j] = index + 1
                for boo in helper2(R, C, board, visited, i, j, my_str, 1, index + 1):
                    boo2 = check_all_words_fit(board, words, visited, index + 1)
                    if boo2:
                        return True
                visited[i][j] = 0

    return False

def main():
    print("Taking in input")
    R = 0
    C = 0
    K = 0
    lens = None
    lens_set = set()
    lens_map = {}
    board = []

    # O(K + RC)
    with open("wordB.in", "r") as f:
        x = [int(i) for i in f.readline().split()]
        R = x[0]
        C = x[1]
        K = x[2]

        lens = [int(i) for i in f.readline().split()]
        for i in lens:
            lens_set.add(i)

        for line in f.readlines():
            temp = []
            my_string = line.rstrip("\n")

            for j in my_string:
                temp.append(j)
            board.append(temp)

    print("board = ", board)
    print("Done with input")
    print("len set = ", lens_set)

    for i in lens_set:
        temp = []
        temp.append(-1)
        lens_map[i] = temp

    print("len map = ", lens_map)
    
    valid_words_0 = prune0(R, C, "wordBwords.txt", lens_set, board)

    print("size of valid_words_0 =", len(valid_words_0))

    valid_words_1 = prune1(R, C, board, valid_words_0)

    print("size of valid words_1 =", len(valid_words_1))

    valid_words_1.sort()

    lens_list = []
    for i in range(K):
        temp = []
        lens_list.append(temp)
    

    lens_sorted = sorted(lens, reverse=True)

    for i in range(K):
        for j in valid_words_1:
            if len(j) == lens_sorted[i]:
                lens_list[i].append(j)

    
    with open("wordB.out", "w") as f:
        for word in valid_words_1:
            f.write(word)
            f.write("\n")
        f.write("Num = ")
        f.write(str(len(valid_words_1)))
        f.write("\n\n\n")

        for i in range(K):
            f.write("len " + str(lens_sorted[i]) + ": ")
            for j in lens_list[i]:
                f.write(j)
                f.write(" ")
            f.write("\n")
        f.write("\n")

    count = [0] * 26
    for i in range(len(board)):
        for j in range(len(board[0])):
            if(board[i][j] != ' '):
                count[ord(board[i][j]) - 65] += 1


    result = []
    recurseAll(board, count, lens_map, lens_list, 0, [], result)
    print("there are:", len(result), "results")

    good_result = []

    for temp in result:
        print("temp =", temp)
    #    print("attemping to check:")

        visited = []
        for i in range(len(board)):
            temp_arr = []
            for j in range(len(board[0])):
                temp_arr.append(0)
            visited.append(temp_arr)

        valid = check_all_words_fit(board, temp, visited, 0)
        print("valid =", valid)
        if valid:
            good_result.append(temp)

            print("and here is visited!")
            printi(visited)

    print(" BUT THERE ARE", len(good_result), "results!")
    for temp_arr in good_result:
        print(temp_arr)

    print("well recurseCalls  =", recurseCalls)
    print("well recurseCalls2 =", recurseCalls2)
    
if __name__ == '__main__':
    main()

'''
3 3 2
4 5
GAT
EMS
SBE

BEST
GAMES

3 3 2
3 6
FRT
IUN
CKY

5 5 5
4 7 7 3 4
MENUS
ABUFE
GEBBL
MSWOR
OEWAD

WORD
BUBBLES
AWESOME
FUN
GAME

3 3 2
4 4
NSI
 ET
TSE

NEST
SITE

7 7 7
5 6 5 5 6 9 8
ESSLUI 
NDLFNFL
NKYEIIE
BIATK R
YEEU ET
ABTCNUS
CHOU  G

YACHT
BOUNCE
GUEST
INFER
LIKELY
BEAUTIFUL
KINDNESS

7 7 7
5 6 8 7 6 8 4
  AKBMA
 LRRSEN
  AREER
MMEUSGC
EOOCTTY
RMTISDU
YSBURNR

STOIC
MEMORY
CEREBRAL
GESTURE
STURDY
MARKSMAN
BURN

3 3 1
8
 NA
TEL
GGP

EGGPLANT

7 7 7
6 4 5 8 7 5 11
NT TANN
IRESIYO
KSENGNT
EEUSKHI
TLROCER
GONPY T
RUMLIF 

GRUMPY
LIFT
ANNOY
SKELETON
THINKER
SCOUR
INTERESTING

7 7 7
8 5 4 7 6 6 8
 EHAHMO
 TIERTN
NFINCYO
IIMALIO
HATE DT
RPO EGA
GCDRR N

INFINITE
TOOTH
CORD
HARMONY
MALICE
DANGER
GRAPHITE

'''
