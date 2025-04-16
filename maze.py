#
# Program 4: Disjoint Sets Applications
#
# Course: CS 351, Spring 2025
# System: MacOS using VS Code
# Author: Kaito Sekiya
# 
# File: maze.py
#
# TODO
#
# Usage:    maze.py [-h] [--n N]
# Example:  maze.py [-h] --n 30
# 


import argparse
from dataclasses import dataclass
from os import makedirs
from PIL import Image, ImageDraw
from random import shuffle
from typing import NamedTuple
from unionfind import UnionFind


FRAMES_DURATION = 1   # Duration each frame is shown (in milliseconds)


# Type hints for the argument parser
@dataclass
class Args:
    n: int # Size of the maze


#
# A `NamedTuple` is a subclass of Python’s built-in `tuple` that lets you define tuples with fields, making the tuple 
# elements more readable. Unlike regular tuples, you can access values by name (e.g., `point.row`) instead of by index.
# 

# Class and type hints for the cell named tuple
class Cell(NamedTuple):
    col: int # Column index (x-coordinate)
    row: int # Row index (y-coordinate)


# Class and type hints for the color named tuple
class Color(NamedTuple):
    r: int # Red component (0–255)
    g: int # Green component (0–255)
    b: int # Blue component (0–255)


#
# Initialize a maze grid and list of walls for randomized Kruskal-style maze generation
#
def init_maze(n: int) -> tuple[list[list[str]], list[tuple[Cell, Cell]]]:
    # Initialize the maze as a solid block
    maze = [['#'] * (2 * n + 1) for _ in range(2 * n + 1)]

    for row in range(n):
        for col in range(n):
            # Each cell is empty
            maze[2 * row + 1][2 * col + 1] = ' ' # 2 * n + 1 since maze includes both walls and cells

    # Create a 2D array representing the walls of the maze
    walls: list[tuple[Cell, Cell]] = []

    for row in range(n):
        for col in range(n):
            # Right wall
            if col + 1 < n: 
                walls.append((Cell(col, row), Cell(col + 1, row))) 
            # Bottom wall
            if row + 1 < n:
                walls.append((Cell(col, row), Cell(col, row + 1)))  
            # No reason to add left and top walls since the border walls already there

    # Shuffle walls to randomize the maze generation
    shuffle(walls)

    return maze, walls


#
# Generate a maze using randomized Kruskal's algorithm and capture frames of its construction
#
def generate_maze(n: int) -> list[Image.Image]:
    # List to store frames for the animation
    frames: list[Image.Image] = []

    # Initialize union-find structure for n x n grid
    maze_uf = UnionFind(n * n)

    # Initialize maze grid and wall list
    maze, walls = init_maze(n)

    # Iterate through the walls and remove them if unioning the cells
    for i, (c1, c2) in enumerate(walls):
        idx1 = c1.row * n + c1.col # Flatten 1D index of first cell
        idx2 = c2.row * n + c2.col # Flatten 1D index of second cell

        # If the cells are not in the same set, remove the wall
        if maze_uf.find(idx1) != maze_uf.find(idx2):
            # Remove the wall between p1 and p2
            if c1.col == c2.col:
                # Vertical wall
                maze[2 * c1.col + 1][2 * c1.row + 2] = ' '
            else: 
                # Horizontal wall
                maze[2 * c1.col + 2][2 * c1.row + 1] = ' '
            
            # Union the two cells
            maze_uf.union(idx1, idx2)

            # Capture a new frame every time a wall is removed
            frames.append(maze_to_image(maze, n))
    
    return frames


#
# Convert the maze grid to its string representation
#
def maze_to_str(maze: list[list[str]]) -> str:
    return '\n'.join([''.join(row) for row in maze])


#
# Convert the maze grid to a PIL image
#
def maze_to_image(
    maze: list[list[str]], 
    n: int,
    cell_size: int = 10, 
    wall_color=Color(0, 0, 0), 
    path_color=Color(255, 255, 255)
) -> Image.Image:
    # Create a blank image filled with wall color
    img = Image.new("RGB", (2 * n * cell_size, 2 * n * cell_size), wall_color)
    # ImageDraw allows to draw on the image
    draw = ImageDraw.Draw(img)

    for y in range(2 * n + 1):
        for x in range(2 * n + 1):
            # If the maze cell is a path (cell or connection between cells), draw it
            if maze[y][x] == ' ':
                x0 = x * cell_size  # Top-left x
                y0 = y * cell_size  # Top-left y
                x1 = x0 + cell_size # Bottom-right x
                y1 = y0 + cell_size # Bottom-right y

                # Draw a rectangle where is the path is
                draw.rectangle([x0, y0, x1, y1], fill=path_color)

    return img


#
# The controlling unit of the program. 
#
def main() -> None:
    # Better sys.argv
    parser = argparse.ArgumentParser()

    parser.add_argument("--n", type=int, default=10, help="Maze size")

    # Parse the command-line arguments
    args: Args = parser.parse_args()

    # Make sure a folder to store GIFs exists
    makedirs("gifs", exist_ok=True)

    # Generate a maze
    frames = generate_maze(args.n)

    # Save the frames as an animated GIF
    frames[0].save(
        f"gifs/maze{args.n}x{args.n}.gif", # Save the maze with dimensions specified in the 'gifs' folder
        save_all=True,
        append_images=frames[1:], # Append subsequent frames
        duration=FRAMES_DURATION, # Set duration per frame
        loop=0                    # Make it an infinite loop
    )

    # Save the last frame (completed maze) as an PNG image
    frames[-1].save(f"images/maze{args.n}x{args.n}.png")


# Just calls main function
if __name__=="__main__":
    main()