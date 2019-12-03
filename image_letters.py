# PIL is PILLOW, the updated Python Imaging Library
from PIL import Image
import os, sys
import queue

# constants of famous colors, represented as triples of RGB values
black = (0, 0, 0)
red = (255, 0, 0)
yellow = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)

# Euclidean norm; sense of how "big" or "bright"
def norm(pixel):
    x = pixel[0]
    y = pixel[1]
    z = pixel[2]
    return x*x + y*y + z*z

# detect if x, y, are in range of 2D array of size A x B
def valid(x, y, A, B):
    if x < 0 or x >= A or y < 0 or y >= B:
        return False
    return True

# directions for BFS traverse
dx = [-1, 0, 1, 0]
dy = [0, 1, 0, -1]

# choose the best letter for this particular block; currently only handles 7 x 7 circles
def get_letter(pixels, x1, y1, x2, y2):
    invalid = [9, 16, 21, 22, 23, 25]

    err = (x2-x1) * (y2 - y1)
    index = -1

    for k in range(26):
        if k in invalid:
            continue
        name = "0" + str(k)
        if k < 10:
            name = "0" + name

        im_let = Image.open("letters/full" + name + ".jpg")
        let_map = im_let.load()

        # images are corrupted or sth; gotta set back to red/black contrast
        for i in range(im_let.size[0]):
            for j in range(im_let.size[1]):
                pxl = let_map[i,j]
                if norm(pxl) > 100*100:
                    let_map[i,j] = (255, 0, 0)
                else:
                    let_map[i,j] = (0, 0, 0)

        # perform bfs on original image to fill in black surrounding circle into red
        q = queue.Queue()
        q.put((x1, y1))
        q.put((x2, y1))
        q.put((x1, y2))
        q.put((x2, y2))

        my_set = set()

        while not q.empty():
            coor = q.get()
            x = coor[0]
            y = coor[1]

            if coor in my_set:
                continue

            my_set.add(coor)

            pixels[x, y] = (255, 0, 0)

            for m in range(4):
                newx = x + dx[m]
                newy = y + dy[m]
                t = (newx, newy)
                if x1 <= newx and newx <= x2 and y1 <= newy and newy <= y2 and pixels[newx, newy] == (0, 0, 0) and t not in my_set:
                    q.put(t)
        #end bfs

        # count errors
        temp_err = 0
        
        for i in range(min(im_let.size[0], x2-x1)):
            for j in range(min(im_let.size[1], y2-y1)):
                pxl1 = pixels[x1 + i, y1 + j]
                pxl2 = let_map[i, j]
                if pxl1 != pxl2:
                    temp_err += 1

        #print("temp err for ", chr(ord('A')  + k), " is ", temp_err)

        # which ever is least is the winner
        if temp_err < err:
            err = temp_err
            index = k

    # return the corresponding character
    return chr(ord('A') + index)


# start here! currently works for wb_00000.jpg and wb_00001.jpg, both 7 x 7 boards
im = Image.open("wb_00002.jpg")
#im.show()
print(im.size)
pixelMap = im.load()

# 7 x 7 bounding box: x: 70, 675 y: 146, 1050
# one bubble has diameter of about 76-78 pixels
# red = (191, 100, 71)

# ngl i have no idea what count is
count = 0

# create a new image as not to modify the original image
imgNew = Image.new(im.mode, im.size)
pixelNew = imgNew.load()

# store coordinates of all character bubbles
bubble_coor = []

# bounding box of all character bubbles
minx = im.size[0]
miny = im.size[1]
maxx = 0
maxy = 0

# black out surroundings
for i in range(im.size[0]):
    for j in range(im.size[1]):

        if 70 <= i and i < 686 and 146 <= j and j < 1050:
            depth = norm(pixelMap[i,j])
            # turn white-ish background into black
            if depth >= 150000:
                pixelNew[i,j] = (0,0,0, 255)
                count += 1
            # turn bottom solution bubbles into white
            elif depth >= 120000:
                pixelNew[i,j] = (255, 255, 255, 255)
            # copy over board bubble colors
            else:
                pixelNew[i,j] = pixelMap[i,j]
        else:
            pixelNew[i,j] = (0, 0, 0, 255)


# get bounding box
for i in range(70 - 10, 686 + 10):
    for j in range(146 - 10, 800 + 10):
        pxl = pixelNew[i,j]
        if (not (pxl == (0,0,0))) and (not (pxl == (255, 255, 255))):
            minx = min(i, minx)
            miny = min(j, miny)
            maxx = max(i, maxx)
            maxy = max(j, maxy)

# remove that annoying thing in the top right corner, which is white, and turn black
for i in range(minx-1, maxx+1):
    for j in range(miny-1, maxy+1):
        pxl = pixelNew[i,j]
        if pxl == (255, 255, 255):
            pixelNew[i,j] = (0, 0, 0, 255)

# turn board bubbles into red
for i in range(minx-1, maxx+1):
    for j in range(miny-1, maxy+1):
        pxl = pixelNew[i,j]
        if (not (pxl == (0,0,0))) and (not (pxl == (255, 255, 255))):
            pixelNew[i,j] = (255, 0, 0, 255)

# make a copy
imgNew_red = Image.new(im.mode, im.size)
pixelNew_red = imgNew_red.load()

for i in range(im.size[0]):
    for j in range(im.size[1]):
        pixelNew_red[i,j] = pixelNew[i,j]

# bounding green box around each bubble in board
for i in range(minx-1, maxx+1):
    for j in range(miny-1, maxy+1):
        pxl = pixelNew[i,j]
        if pxl == red:
            #x1 y1 x2 y2 are coordinates of bounding box
            x1 = i
            y1 = j
            x2 = i
            y2 = j

            x = i
            y = j

            in_list = set()

            q = queue.Queue()
            q.put((x, y))

            while not q.empty():
                coor = q.get()
       #         print("coor = ", coor)
                pixelNew[coor[0], coor[1]] = yellow

                x1 = min(coor[0], x1)
                x2 = max(coor[0], x2)
                y1 = min(coor[1], y1)
                y2 = max(coor[1], y2)

                if (coor[0]+1, coor[1]) not in in_list and pixelNew[coor[0] + 1, coor[1]] == red:
                    q.put((coor[0] + 1, coor[1]))
                    in_list.add((coor[0]+1, coor[1]))
                if (coor[0]-1, coor[1]) not in in_list and pixelNew[coor[0] - 1, coor[1]] == red:
                    q.put((coor[0] - 1, coor[1]))
                    in_list.add((coor[0]-1, coor[1]))
                if (coor[0], coor[1] + 1) not in in_list and pixelNew[coor[0], coor[1] + 1] == red:
                    q.put((coor[0], coor[1] + 1))
                    in_list.add((coor[0], coor[1] + 1))
                if (coor[0], coor[1] - 1) not in in_list and pixelNew[coor[0], coor[1] - 1] == red:
                    q.put((coor[0], coor[1] - 1))
                    in_list.add((coor[0], coor[1] - 1))

            #print(x2 - x1, y2 - y1)

            if (x2-x1) * (y2 - y1) < 100:
                # area is too small; for some reason this occurred; must be an error
                continue

            t = ((x1, y1), (x2, y2))
            print("gonna add t =", t)
            bubble_coor.append(t)

            for i in range(x1, x2):
                for j in range(y1, y2):
                    pixelNew[i, j] = (0, 255, 0)

# 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25
# A B C D E F G H I J  K  L  M  N  O  P  Q  R  S  T  U  V  W  X  Y  Z


# get how big the actual board is; i'm also thinking of doing sth else for this
side_len = 1
while side_len * side_len < len(bubble_coor):
    side_len += 1

board = []
for i in range(side_len):
    temp = []
    for j in range(side_len):
        temp.append(' ')
    board.append(temp)

# minimum error
for i in range(len(bubble_coor)):
    top_left = bubble_coor[i][0]
    bot_right = bubble_coor[i][1]
    x1 = top_left[0]
    y1 = top_left[1]
    x2 = bot_right[0]
    y2 = bot_right[1]

    result = get_letter(pixelNew_red, x1, y1, x2, y2)

    # since row / col are swapped in Pillow,
    bubble_len = (x2-x1) + 10
    col = round((x1 - minx) / bubble_len)
    row = round((y1 - miny) / bubble_len)

    print("access [", col, row, "]")
    print("temp_result =", result)

    board[row][col] = result

for i in range(len(board)):
    print(board[i])

#imgNew.show()
imgNew_red.show()

#print("count =", count)
#print("top left = (", minx, ",", miny, ") and bot right = (", maxx, ",", maxy, ")")
print("side_len =", side_len)
print("board =", board)
