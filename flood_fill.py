#
# Program 4: Disjoint Sets Applications
#
# Course: CS 351, Spring 2025
# System: MacOS using VS Code
# Author: Kaito Sekiya
# 
# File: flood_fill.py
#
# Flood fill algorithm implementation that fills a region in an image starting from a specified point. 
# Supports Union-Find, stack, and queue methods for flood filling, and generates an animated GIF of the process.
#
# Usage:    flood_fill.py [-h] [--mode MODE] image target color
# Example:  flood_fill.py [-h] images/uic.png 50,50 255,0,0 --mode stack
# 


import argparse
from collections import deque
from dataclasses import dataclass
from os import makedirs
from pathlib import Path
from PIL import Image
from typing import NamedTuple
from unionfind import UnionFind


FRAMES_INTERVAL = 200 # Pixels changed between frames taken during flood fill
FRAMES_LIMIT    = 200 # Max number of frames to animate the flood fill
FRAMES_DURATION = 1   # Duration each frame is shown (in milliseconds)


# Type hints for the argument parser
@dataclass
class Args:
    image: str        # Path to the image to flood fill
    start: tuple[int] # Starting point for the flood fill (row, col)
    color: tuple[int] # Fill color as an (R, G, B) tuple
    ds:    str        # Data structure ('unionfind', 'stack', or 'queue') to use in the flood fill


#
# A `NamedTuple` is a subclass of Python’s built-in `tuple` that lets you define tuples with fields, making the tuple 
# elements more readable. Unlike regular tuples, you can access values by name (e.g., `point.row`) instead of by index.
# 

# Class and type hints for the point named tuple
class Point(NamedTuple):
    col: int # Column index (x-coordinate)
    row: int # Row index (y-coordinate)


# Class and type hints for the color named tuple
class Color(NamedTuple):
    r: int # Red component (0–255)
    g: int # Green component (0–255)
    b: int # Blue component (0–255)


#
# Computes and compares the squared Euclidean distance between two points in the RGB color space.
#
def is_similar_color(p1: Color, p2: Color, threshold: int = 300) -> bool:
    return (p1.r - p2.r) ** 2 + (p1.g - p2.g) ** 2 + (p1.b - p2.b) ** 2 <= threshold


#
# Group adjacent pixels in an image by color similarity
#
def union_pixels_by_color(img: Image.Image) -> UnionFind:
    img_uf = UnionFind(img.width * img.height) 

    for row in range(img.height):
        for col in range(img.width):
            # Flatten 1D index from 2D coordinates
            idx = row * img.width + col 

            neighbors = []

            # Left neighbor
            if col - 1 >= 0:
                neighbors.append((col - 1, row))
            # Right neighbor
            if col + 1 < img.width:
                neighbors.append((col + 1, row))
            # Top neighbor
            if row - 1 >= 0:
                neighbors.append((col, row - 1))
            # Bottom neighbor
            if row + 1 < img.height:
                neighbors.append((col, row + 1))

            if len(neighbors) != 0:
                # Color of the current cell
                color = Color(*img.getpixel((col, row))) 
                
                for col_n, row_n in neighbors:
                    # Union if the neighbor cell has similar color
                    if is_similar_color(color, Color(*img.getpixel((col_n, row_n)))):
                        img_uf.union(idx, row_n * img.width + col_n)

    return img_uf 


#
# Flood fills the image by using union-find
#
def union_find_flood_fill(
    img: Image.Image, # Image to flood file
    start: Point,     # Starting position of the flood fill
    color: Color      # Data structure to use in the flood fill 
) -> list[Image.Image]:
    # List to store frames for the animation
    frames: list[Image.Image] = []

    # Get the union-find with pixels grouped by color
    img_uf = union_pixels_by_color(img)
    # Get the parent of the start pixel
    parent = img_uf.find(start.row * img.width + start.col) # uses flatten 1D index from 2D coordinates

    for row in range(img.height):
        for col in range(img.width):
            # Flatten 1D index from 2D coordinates
            idx = row * img.width + col

            # Update color to the given one if pixel belongs to same set as the start pixel
            if img_uf.find(idx) == parent:
                img.putpixel((col, row), color)

            # Capture a new frame every FRAMES_INTERVAL pixels
            if idx % FRAMES_INTERVAL == 0:
                frames.append(img.copy())

    return frames


#
# Uses queue (BFS) or stack (DFS) to flood fill the image with the given color from the given starting position
#
def recursive_flood_fill(
    img: Image.Image, # Image to flood fill
    start: Point,     # Starting position of the flood fill
    color: Color,     # Fill color
    ds: str           # Data structure to use in the flood fill   
) -> list[Image.Image]:
    # List to store frames for the animation
    frames: list[Image.Image] = []

    # Deque can be used as both queue and stack
    queue_stack: deque[Point] = deque()
    # Start with the start pixel, makes sense, right?
    queue_stack.append(start)

    # Get the color of the start pixel to compare against neighbors color
    start_color = Color(*img.getpixel(start))

    # Frame counter to manage interval
    frames_timer = 0

    # Continue until structure is empty
    while len(queue_stack) != 0:
        # Pop from front if queue, back if stack
        point = queue_stack.popleft() if ds == "queue" else queue_stack.pop() # if mode == "stack"
        # Get color of current pixel
        point_color = Color(*img.getpixel(point))

        # Check if the color matches the start pixel
        if is_similar_color(start_color, point_color):
            # Update the current pixel with a new color
            img.putpixel((point.col, point.row), color)
            
            # Left neighbor
            if point.col - 1 >= 0:
                queue_stack.append(Point(point.col - 1, point.row))
            # Right neighbor
            if point.col + 1 < img.width:
                queue_stack.append(Point(point.col + 1, point.row))
            # Top neighbor
            if point.row - 1 >= 0:
                queue_stack.append(Point(point.col, point.row - 1))
            # Bottom neighbor
            if point.row + 1 < img.height:
                queue_stack.append(Point(point.col, point.row + 1))

        # Capture a new frame every FRAMES_INTERVAL pixels
        if frames_timer % FRAMES_INTERVAL == 0:
            frames.append(img.copy())

        frames_timer += 1

    return frames


#
# Converts a comma-separated string into a tuple of integers
#
def to_tuple(arg: str) -> tuple[int]:
    return tuple(map(int, arg.split(',')))


#
# Evenly reduces the number of frames to the given limit
#
def evenly_limit_frames(frames: list, limit: int = 500) -> list[Image.Image]:
    # Return the number is less than the limit
    if len(frames) <= limit:
        return frames 

    # Calculate step size to space frames evenly
    step = len(frames) / limit
    # Rebuild list with the given number of evenly spaced frames
    return [frames[int(i * step)] for i in range(limit)]


#
# The controlling unit of the program. 
#
def main() -> None:
    # Better sys.argv
    parser = argparse.ArgumentParser()

    parser.add_argument("image", type=str, help="Path to the image to flood fill")
    parser.add_argument("start", type=to_tuple, help="Starting point for the flood fill (e.g. 0,0)")
    parser.add_argument("color", type=to_tuple, help="Fill color (e.g. 255,0,0)")
    parser.add_argument("--ds", type=str, default="unionfind", help="Data structure to use in the flood fill")

    # Parse the command-line arguments
    args: Args = parser.parse_args()

    # Make sure a folder to store GIFs exists
    makedirs("gifs", exist_ok=True)

    # Open the image to flood fill
    img: Image.Image = Image.open(args.image).convert("RGB")

    # Based on the abstact data structure (or ADT) selected, flood fill with:
    if args.ds == "unionfind":
        # Union-find
        frames = union_find_flood_fill(img, Point(*args.start), Color(*args.color))
    elif args.ds == "stack" or args.ds == "queue":
        # Recursion and stack/queue
        frames = recursive_flood_fill(img, Point(*args.start), Color(*args.color), args.ds)

    # Limit the number of frames to the specified limit
    frames = evenly_limit_frames(frames, FRAMES_LIMIT)

    # Save the frames as an animated GIF
    frames[0].save(
        f"gifs/{Path(args.image).stem}-{args.ds}.gif", # Save with the same name as the image but in the 'gifs' folder
        save_all=True,
        append_images=frames[1:], # Append subsequent frames
        duration=FRAMES_DURATION, # Set duration per frame
        loop=0                    # Make it an infinite loop
    )

    
# Just calls main function
if __name__=="__main__":
    main()