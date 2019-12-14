# Word Popper

## Group Members
Kevin Hao\n
Aditi Jain\n
Brian Wang\n
Jesse Zou\n

## Objective
We are given a picture of a puzzle from WordBubbles!. This image contains a two-dimensional grid of english characters and blanks. There is also several rows of empty blanks that represent the lengths of the desired words. We have to find a set of english words with these specified lengths such that each english word can be "found" in the matrix, and every character in the matrix is used exactly once. An english word can be found in the matrix when every letter in the word is in the board, and every letter is adjancent to its neighbors in one of the eight directions.

## Files
solve.py - Python script to take in an image and output all possible sets of answers and their orientations.

requirements.txt - contains libraries that need to be downloaded - PILLOW for image parsing

allWords.txt - contains the dictionary of all possible english words

puzzles - a directory containing images of puzzles to be solved

Run this to check dependencies: 
`pip install -r requirements.txt`  

To run the program:
`python3 solve.py <image_name>`

ex. `python3 solve.py IMG_01`