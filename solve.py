#!/usr/bin/env python
# coding: utf-8


# PIL is PILLOW, the updated Python Imaging Library.
from PIL import Image, ImageDraw, ImageColor
import os
import sys
import queue
import math
import time


# These are colors represented as triples of RGB values.
black = (0, 0, 0, 255)
red = (255, 0, 0, 255)
green = (0, 255, 0, 255)
blue = (0, 0, 255, 255)
white = (255, 255, 255, 255)

# These are the directions for BFS traverse.
dx = [-1, 0, 1, 0]
dy = [0, 1, 0, -1]

# The 8 directions for traversing a board.
dr = [-1, -1, -1, 0, 1, 1,  1,  0]
dc = [-1,  0,  1, 1, 1, 0, -1, -1]


def in_bounds(x, y, R, C):
    """Checks if an x,y coordinate is in a R x C board."""
    return (0 <= x and x < R and 0 <= y and y < C)


def bfs(pixels, points, x1, y1, x2, y2, search_color, new_color):
    """Performs a breadth-first search in the bounding box (x1, y1) to
    (x2, y2). The BFS starts with points and changes all pixels of
    search_color to new_color. Returns a bounding box.
    """
    minx = x2
    miny = y2
    maxx = x1
    maxy = y1

    # Add points to a Queue.
    q = queue.Queue()
    for point in points:
        if x1 <= point[0] and point[0] <= x2 and y1 <= point[1] and \
                point[1] <= y2 and pixels[point[0], point[1]] == search_color:
            minx = min(point[0], minx)
            miny = min(point[1], miny)
            maxx = max(point[0], maxx)
            maxy = max(point[1], maxy)
            q.put(point)

    visited = set()
    while not q.empty():
        point = q.get()
        x = point[0]
        y = point[1]

        minx = min(point[0], minx)
        miny = min(point[1], miny)
        maxx = max(point[0], maxx)
        maxy = max(point[1], maxy)

        if point in visited:
            continue

        visited.add(point)
        pixels[x, y] = new_color
        for k in range(4):
            newx = x + dx[k]
            newy = y + dy[k]
            if x1 <= newx and newx <= x2 and y1 <= newy and newy <= y2 \
                    and pixels[newx, newy] == search_color:
                q.put((newx, newy))

    return ((minx, miny), (maxx, maxy))


def get_row_nums(pixels, x1, y1, x2, y2):
    """Finds the number of groups of black pixels in a given row.
    This helps distinguish between different letters.
    """
    ans = []
    for i in range(y1, y2 + 1):
        temp = 0
        for j in range(x1 + 1, x2 + 1):
            if pixels[j - 1, i] == green and pixels[j, i] == black:
                temp += 1
        if temp != 0 and (len(ans) == 0 or ans[-1] != temp):
            ans.append(temp)

    return ans


def get_col_nums(pixels, x1, y1, x2, y2):
    """Finds the number of groups of black pixels in a given column.
    This helps distinguish between different letters
    """
    ans = []
    for i in range(x1, x2 + 1):
        temp = 0
        for j in range(y1 + 1, y2 + 1):
            if pixels[i, j - 1] == green and pixels[i, j] == black:
                temp += 1
        if temp != 0 and (len(ans) == 0 or ans[-1] != temp):
            ans.append(temp)

    return ans


def get_letter(pixels, x1, y1, x2, y2, bpixel_count):
    """Determines a character based on the number of groups of black pixels in
    the rows and columns. Characters with nondistinct identities are
    determined using total pixel count. If their total pixel count is not
    unique, unique pixel locations inside the bounding box of the character
    are used to determine the character.
    e.g. (an R has a higher pixel count than an A)
    e.g. (an L has no pixel in the upper right corner in its bounding box,
    but a T does)
    """

    row_nums = get_row_nums(pixels, x1, y1, x2, y2)
    col_nums = get_col_nums(pixels, x1, y1, x2, y2)

    if row_nums == [1, 2, 1, 2, 1] and col_nums[0:3] == [1, 3, 2]:
        return 'B'
    if row_nums == [1, 2, 1, 2, 1] and col_nums == [1, 2, 1]:
        return 'C'
    if row_nums == [1] and col_nums == [1, 3, 2, 1]:
        return 'E'
    if row_nums == [1] and col_nums == [1, 2, 1]:
        return 'F'
    if row_nums == [2, 1, 2] and col_nums == [1]:
        return 'H'
    if row_nums == [1, 2, 1] and col_nums == [1]:
        return 'J'
    if row_nums == [2, 1, 2] and col_nums == [1, 2, 1]:
        return 'K'
    if row_nums == [2, 4, 3, 2]:
        return 'M'
    if row_nums == [2, 3, 2]:
        return 'N'
    if row_nums == [1, 2, 1] and col_nums == [1, 2, 3, 2, 1]:
        return 'Q'
    if row_nums == [3, 4, 2]:
        return 'W'
    if row_nums == [2, 1, 2]:
        return 'X'
    if row_nums == [1] and 3 in col_nums and 2 in col_nums:
        return 'Z'

    x3 = x2
    y3 = y2
    x4 = x1
    y4 = y1

    for i in range(x1, x2+1):
        for j in range(y1, y2+1):
            if pixels[i, j] == black:
                small_box = bfs(pixels, ((i, j),), x1, y1, x2, y2, black, red)
                x3 = min(small_box[0][0], x3)
                y3 = min(small_box[0][1], y3)
                x4 = max(small_box[1][0], x4)
                y4 = max(small_box[1][1], y4)

    if row_nums == [1, 2, 1, 2] and col_nums == [1, 2, 1]:
        if (pixels[x3, y3] == red or pixels[x3 + 1, y3] == red or
                pixels[x3, y3+1] == red or pixels[x3 + 1, y3+1] == red):
            return 'R'
        else:
            return 'A'

    if row_nums == [1, 2, 1, 2]:
        return 'R'

    if row_nums == [1, 2, 1, 2, 1] and col_nums == [1, 2, 3, 2, 1]:
        avgy = (y3+y4)//2
        if (pixels[x3, avgy] == red or pixels[x3, avgy - 1] == red or
                pixels[x3, avgy + 1] == red):
            return 'G'
        return 'S'

    if row_nums == [1] and col_nums == [1]:
        if ((pixels[x4, y3] == red or pixels[x4 - 1, y3] == red or
            pixels[x4, y3+1] == red or pixels[x4 - 1, y3 + 1] == red) and
            (pixels[x4, y4] == red or pixels[x4-1, y4] == red or
                pixels[x4, y4 - 1] == red or pixels[x4-1, y4-1] == red)):
            return 'I'
        elif pixels[x3, y4] == red or pixels[x3 + 1, y4] == red or \
                pixels[x3, y4 - 1] == red or pixels[x3 - 1, y4 - 1] == red:
            return 'L'
        return 'T'

    if row_nums == [1, 2, 1] and col_nums == [1, 2, 1]:
        avgy = (y3 + y4) // 2
        avgx = (x3 + x4) // 2
        if pixels[avgx, avgy + int(1/13 * (y4 - y3))] == red:
            return 'P'
        if pixels[x3, y4] == red or pixels[x3 + 1, y4] == red or \
                pixels[x3, y4 - 1] == red or pixels[x3 - 1, y4 - 1] == red:
            return 'D'
        return 'O'

    if row_nums == [2, 1] and col_nums == [1]:
        avgy = (y3 + y4) // 2
        if (pixels[x3, avgy] == red or pixels[x3, avgy-1] == red or
                pixels[x3, avgy+1] == red):
            return 'U'
        avgx = (x3 + x4) // 2
        if (pixels[avgx, avgy] == red):
            return 'Y'
        return 'V'

    return '?'


def print_board(board, start_space=""):
    """This method prints the elements of the board."""
    print(start_space + "-" * ((len(board[0][0]) + 1) * len(board[0]) + 3))
    for row in board:
        print(start_space + "|", end=" ")
        for elem in row:
            print(elem, end=" ")
        print("|")

    print(start_space + "-" * ((len(board[0][0]) + 1) * len(board[0]) + 3))


def get_input(name=None):
    """This method retrieves a PNG file of the WordBubbles! puzzle and
    obtain the character matrix, the mapping from pixels to row / col, and
    the lengths needed to solve the puzzle.
    """
    if name is None:
        print("no input picture")
        sys.exit(-1)

    img = Image.open(name)
    pixels = img.load()
    img_1 = Image.new(img.mode, img.size)
    pixels_1 = img_1.load()

    print("loading image...\n[", end="")
    print("L", end="", flush=True)

    for i in range(img.size[0]):
        for j in range(img.size[1]):
            pxl = pixels[i, j]
            if (pxl[0] >= 251 and pxl[2] >= 251):
                pixels_1[i, j] = black
            elif (pxl[0] <= 155 or pxl[1] <= 155 or pxl[2] <= 155):
                pixels_1[i, j] = red
            elif 200 <= pxl[0] and pxl[0] <= 228 and 200 <= pxl[1] and \
                    pxl[1] <= 228 and 200 <= pxl[2] and pxl[2] <= 228:
                pixels_1[i, j] = white
            else:
                pixels_1[i, j] = blue

    box_top = ((0, 240), (img.size[0], img.size[1]//2 + 160))
    box_bot = ((0, img.size[1]//2 + 160), (img.size[0], img.size[1] - 480))

    print("O", end="", flush=True)
    print("A", end="", flush=True)

    bubble_box = []
    for i in range(box_top[0][0], box_top[1][0], 15):
        for j in range(box_top[0][1], box_top[1][1], 15):
            if pixels_1[i, j] == red:
                box_small = bfs(pixels_1, ((i, j),), box_top[0][0],
                                box_top[0][1], box_top[1][0], box_top[1][1],
                                red, green)
                if((box_small[1][0] - box_small[0][0]) > 90):
                    bubble_box.append(box_small)

    print("D", end="", flush=True)

    for box in bubble_box:
        x1 = box[0][0]
        y1 = box[0][1]
        x2 = box[1][0]
        y2 = box[1][1]

        points = ((x1, y1), (x1, y2), (x2, y1), (x2, y2))
        for i in range(x1, x2+1):
            for j in range(y1, y2+1):
                if pixels_1[i, j] != black:
                    pixels_1[i, j] = green

    little_box = []
    print("I", end="", flush=True)

    for i in range(box_bot[0][0], box_bot[1][0]):
        for j in range(box_bot[0][1], box_bot[1][1]):
            if pixels_1[i, j] == white:
                box_small = bfs(pixels_1, ((i, j),), box_bot[0][0],
                                box_bot[0][1], box_bot[1][0], box_bot[1][1],
                                white, black)
                little_box.append(box_small)

    print("N", end="", flush=True)

    y_to_length = {}
    for box in little_box:
        x1 = box[0][0]
        y1 = box[0][1]
        x2 = box[1][0]
        y2 = box[1][1]

        for i in range(x1, x2+1):
            for j in range(y1, y2+1):
                pixels_1[i, j] = blue

        if (len(y_to_length) == 0):
            y_to_length[y1] = 1
        else:
            valid = False
            for key in y_to_length:
                if abs(key - y1) <= 10:
                    y_to_length[key] += 1
                    valid = True
                    break
            if not valid:
                y_to_length[y1] = 1

    lens = []
    for key in y_to_length:
        lens.append(y_to_length[key])

    side_length = 0
    while (side_length) ** 2 < len(bubble_box):
        side_length += 1

    bubble_size = (bubble_box[0][1][0] - bubble_box[0][0][0])

    bpixel_count = []
    for i in range(side_length):
        temp = []
        for j in range(side_length):
            temp.append(0)
        bpixel_count.append(temp)

    board = []
    for i in range(side_length):
        temp = []
        for j in range(side_length):
            temp.append(' ')
        board.append(temp)

    pixel_to_rc = {}
    minx = 1000000
    miny = 1000000
    maxx = 0
    maxy = 0

    # find bounding box of top again
    for box in bubble_box:
        x1 = box[0][0]
        y1 = box[0][1]
        x2 = box[1][0]
        y2 = box[1][1]

        minx = min(x1, minx)
        miny = min(y1, miny)
        maxx = max(x2, maxx)
        maxy = max(y2, maxy)

    # do mapping and count # of black pixels
    for box in bubble_box:
        x1 = box[0][0]
        y1 = box[0][1]
        x2 = box[1][0]
        y2 = box[1][1]

        row = (y1 - miny) // (bubble_size + 10)
        col = (x1 - minx) // (bubble_size + 10)
        pixel_to_rc[box[0]] = (row, col)

        temp = 0
        for i in range(x1, x2 + 1):
            for j in range(y1, y2 + 1):
                if pixels_1[i, j] == black:
                    temp += 1

        bpixel_count[row][col] = temp

    print("'", end="", flush=True)

    for box in bubble_box:
        x1 = box[0][0]
        y1 = box[0][1]
        x2 = box[1][0]
        y2 = box[1][1]

        row_nums = get_row_nums(pixels_1, x1, y1, x2, y2)
        col_nums = get_col_nums(pixels_1, x1, y1, x2, y2)

        row, col = pixel_to_rc[box[0]]
        board[row][col] = get_letter(pixels_1, x1, y1, x2, y2,
                                     bpixel_count[row][col])

    print("]")
    print("This is the board:")
    print_board(board, "\t")

    return board, pixel_to_rc, lens


def get_word_from_file(lens, name="allWords.txt"):
    """This method gets english words from a dictionary text file."""
    with open(name, "r") as f:
        for line in f.readlines():
            line = line.rstrip("\n")
            word = line.upper()
            if len(word) in lens:
                yield word


def triplet_prune(board, lens):
    """Removes words that contain triplets not found in the board."""
    my_set = set()
    R = len(board)
    C = len(board[0])
    for i in range(R):
        for j in range(C):
            for k in range(8):
                i1 = i + dr[k]
                j1 = j + dc[k]
                if in_bounds(i1, j1, R, C):
                    for m in range(8):
                        i2 = i1 + dr[m]
                        j2 = j1 + dc[m]
                        if (not (i2 == i and j2 == j) and
                                in_bounds(i2, j2, R, C)):
                            if board[i][j] != ' ' and board[i1][j1] != ' '\
                             and board[i2][j2] != ' ':
                                my_set.add(board[i][j] + board[i1][j1] +
                                           board[i2][j2])

    ans = []
    for word in get_word_from_file(lens):
        valid = True
        for j in range(2, len(word)):
            key = word[j-2] + word[j-1] + word[j]
            if key not in my_set:
                valid = False
                break
        if valid:
            ans.append(word)

    return ans


def check_word(board, word, word_to_location, r, c, visited, index, cur_list):
    """Checks if the word exists in the board."""
    if(index >= len(word)):
        if word not in word_to_location:
            word_to_location[word] = []
        new_list = []
        for coord in cur_list:
            new_list.append(coord)
        word_to_location[word].append(new_list)
        return
    for i in range(8):
        new_r = r + dr[i]
        new_c = c + dc[i]
        if in_bounds(new_r, new_c, len(board), len(board)):
            if not visited[new_r][new_c]:
                if board[new_r][new_c] is word[index]:
                    visited[new_r][new_c] = True
                    cur_list.append((new_r, new_c))
                    check_word(board, word, word_to_location, new_r,
                               new_c, visited, index + 1, cur_list)
                    cur_list.remove((new_r, new_c))
                    visited[new_r][new_c] = False


def find_word(board, word, word_to_location):
    """Locates all possible starting locations of a word within the board."""
    visited = []
    for i in range(len(board)):
        visited.append([False] * len(board))
    for r, row in enumerate(board):
        for c, char in enumerate(row):
            if (char is word[0]):
                visited[r][c] = True
                coord_list = []
                coord_list.append((r, c))
                check_word(board, word, word_to_location, r, c,
                           visited, 1, coord_list)
                visited[r][c] = False


def get_length_map(word_to_location):
    """This method creates a map that maps lengths of words to words."""
    length_to_words = {}
    for word in word_to_location:
        if not len(word) in length_to_words:
            length_to_words[len(word)] = []
        length_to_words[len(word)].append(word)
    return length_to_words


def frequency_pruning(freqs, lens, length_to_words, index,
                      pruned_list, cur_words, length_to_index):
    """A recursive method that determines which set of words are possible
    given the character count on the board.
    """
    if (index >= len(lens)):
        new_words = []
        for word in cur_words:
            new_words.append(word)
        pruned_list.append(new_words)
        return

    for i in range(length_to_index[lens[index]],
                   len(length_to_words[lens[index]])):
        word = length_to_words[lens[index]][i]
        valid = True
        for char in word:
            freqs[ord(char) - ord('A')] -= 1
        for char in word:
            if freqs[ord(char) - ord('A')] < 0:
                valid = False
                break

        if valid:
            cur_words.append(word)
            before = length_to_index[lens[index]]
            length_to_index[lens[index]] = i + 1
            frequency_pruning(freqs, lens, length_to_words, index + 1,
                              pruned_list, cur_words, length_to_index)
            length_to_index[lens[index]] = before
            cur_words.remove(word)

        for char in word:
            freqs[ord(char) - ord('A')] += 1


def non_overlapping_solution(word_list, word_to_location, index, prev_set,
                             solution, solutions):
    """Returns solutions that contain non-overlapping coordinates such that
    this solution is actually valid.
    """
    if index >= len(word_list):
        new_sol = []
        for s in solution:
            new_sol.append(s)
        if str(word_list) not in solutions:
            solutions[str(word_list)] = []
        solutions[str(word_list)].append(new_sol)
        return

    for locations in word_to_location[word_list[index]]:
        new_set = prev_set.union(set(locations))
        if len(new_set) is len(prev_set) + len(locations):
            solution.append(locations)
            non_overlapping_solution(word_list, word_to_location, index + 1,
                                     new_set, solution, solutions)
            solution.remove(locations)


def main():
    start = time.time()
    file_name = sys.argv[1]
    lens = []
    lens_set = set()
    board = []
    board, pixel_to_rc, lens = get_input("puzzles/" + file_name + ".PNG")

    end = time.time()
    print("Loaded in %.2f seconds\n" % (end-start))

    start = time.time()

    print("solving puzzle...")
    print("[", end="", flush=True)

    lens_set = set(lens)
    lens.sort(reverse=True)
    pruned_list = triplet_prune(board, lens)

    print("S", end="", flush=True)

    word_to_location = {}
    for word in pruned_list:
        find_word(board, word, word_to_location)

    print("O", end="", flush=True)

    length_to_words = get_length_map(word_to_location)

    print("L", end="", flush=True)

    freqs = []
    for i in range(26):
        freqs.append(0)

    print("V", end="", flush=True)

    for row in board:
        for char in row:
            if (char != ' '):
                freqs[ord(char) - ord('A')] += 1

    print("I", end="", flush=True)

    pruned_list = []
    length_to_index = {}
    for length in lens_set:
        length_to_index[length] = 0

    frequency_pruning(freqs, lens, length_to_words, 0,
                      pruned_list, [], length_to_index)

    print("N", end="", flush=True)

    end = time.time()
    solutions = {}
    for p in pruned_list:
        non_overlapping_solution(p, word_to_location, 0, set(), [], solutions)

    print("']")

    for word_list in solutions:
        print("\nWe found this solution: ", word_list)
        print("With these orientations: ")
        for solution in solutions[word_list]:
            index = 0
            new_board = []
            for i in range(len(board)):
                new_board.append(["   "] * len(board[0]))

            for tuples in solution:
                for i, t in enumerate(tuples):
                    if i + 1 > 9:
                        new_board[t[0]][t[1]] = chr(ord("A") + index)\
                         + str(i+1)
                    else:
                        new_board[t[0]][t[1]] = chr(ord("A") + index)\
                         + str(i+1) + " "
                index += 1

            print_board(new_board, "\t")

    end = time.time()
    print("Solved in %.2f seconds" % (end-start))

if __name__ == '__main__':
    main()
