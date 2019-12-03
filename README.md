# Word Popper

## Problem
We are given a two-dimensional matrix of english characters. We have to find a set of english words with some specified lengths such that each english word can be "found" in the matrix, and every character in the matrix is used exactly once. An english word can be found in the matrix when every letter in the word is in the board, and every letter is adjancent to its neighbors in one of the eight directions.

## Solution


## Files
image_letters.py provides the conversion from WordBubbles puzzle image into the matrix of characters. As of now, it only works with 7x7 boards and boards that do not have the characters J, Q, V, W, X, or Z (I have not encountered them yet). It also requires PILLOW, a Python imaging package that I personally found tricky to install on Windows.

wb_0000#.jpg are some WordBubbles screenshots. wb_00002 is a 2x2 board, and the rest are 7x7 boards (provided by WordBubble's weekly challenges).

wordB.py is the actual Python source code that converts matrix of characters into possible solutions. We can always scrap this and redo it as a group; this is BACKUP ONLY in case we run out of time.

wordB.in / wordB.out are input / output. You paste the puzzle you want into wordB.in. wordB.out will show some informative information. The actual solution it finds is printed into standard out. Some examples of puzzles are found at the bottom of wordB.py (copy-paste into wordB.in)

wordBwords.txt contains the current list of english words it checks. Will need to be updated as it is not complete.
