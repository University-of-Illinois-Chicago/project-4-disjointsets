#
# Program 4: Disjoint Sets Applications
#
# Course: CS 351, Spring 2025
# System: MacOS using VS Code
# Author: Kaito Sekiya
# 
# File: flood_fill.py
#
# TODO: description
#
# Usage:    flood_fill.py [-h] [--mode MODE] image target color
# Example:  flood_fill.py [-h] images/uic.png 50,50 255,0,0 --mode stack
# 


import argparse
from collections import deque
from dataclasses import dataclass
from unionfind import UnionFind
from pathlib import Path
from PIL import Image
from typing import NamedTuple
from os import makedirs


TIMER = 200
DURATION = 1


@dataclass
class Args:
    image:  str
    target: tuple[int]
    color:  tuple[int]
    mode:   str


class Point(NamedTuple):
    col: int
    row: int


class Color(NamedTuple):
    r: int
    g: int
    b: int


#
# Computes and compares the squared Euclidean distance between two points in the RGB color space.
#
def is_similar_color(p1: Color, p2: Color, threshold: int = 300) -> bool:
    return (p1.r - p2.r) ** 2 + (p1.g - p2.g) ** 2 + (p1.b - p2.b) ** 2 <= threshold


#
#
#
def union_pixels_by_color(img: Image.Image) -> UnionFind:
    img_ds = UnionFind(img.width * img.height)

    for row in range(img.height):
        for col in range(img.width):
            idx = row * img.width + col
            color = Color(*img.getpixel((col, row)))

            adjacent = []

            #
            if col - 1 >= 0:
                adjacent.append((col - 1, row))
            #
            if col + 1 < img.width:
                adjacent.append((col + 1, row))
            #
            if row - 1 >= 0:
                adjacent.append((col, row - 1))
            #
            if row + 1 < img.height:
                adjacent.append((col, row + 1))
            
            for col_a, row_a in adjacent:
                if is_similar_color(color, Color(*img.getpixel((col_a, row_a)))):
                    img_ds.union(idx, row_a * img.width + col_a)

    return img_ds


#
#
#
def disjoint_sets_flood_fill(
    img: Image.Image,
    target: Point,
    color: Color
) -> list[Image.Image]:
    #
    frames: list[Image.Image] = []

    #
    img_ds = union_pixels_by_color(img)
    #
    parent = img_ds.find(target.row * img.width + target.col)

    #
    for row in range(img.height):
        #
        for col in range(img.width):
            #
            idx = row * img.width + col

            #
            if img_ds.find(idx) == parent:
                img.putpixel((col, row), color)

            #
            if idx % TIMER == 0:
                frames.append(img.copy())

    return frames


#
#
#
def recursive_flood_fill(
    img: Image.Image,
    target: Point,
    color: Color,
    mode: str
) -> list[Image.Image]:
    #
    frames: list[Image.Image] = []

    #
    queue_stack: deque[Point] = deque()
    #
    queue_stack.append(target)

    #
    target_color = Color(*img.getpixel(target))

    #
    frames_timer = 0

    #
    while len(queue_stack) != 0:
        #
        point = queue_stack.popleft() if mode == "queue" else queue_stack.pop() # if mode == "stack"

        # 
        if is_similar_color(target_color, Color(*img.getpixel(point))):
            #
            img.putpixel((point.col, point.row), color)

            if frames_timer % TIMER == 0:
                frames.append(img.copy())
            
            #
            if point.col - 1 >= 0:
                queue_stack.append(Point(point.col - 1, point.row))
            #
            if point.col + 1 < img.width:
                queue_stack.append(Point(point.col + 1, point.row))
            #
            if point.row - 1 >= 0:
                queue_stack.append(Point(point.col, point.row - 1))
            #
            if point.row + 1 < img.height:
                queue_stack.append(Point(point.col, point.row + 1))

        frames_timer += 1

    return frames


#
#
#
def to_tuple(arg: str) -> tuple[int]:
    return tuple(map(int, arg.split(',')))


#
# The controlling unit of the program. 
#
def main() -> None:
    #
    parser = argparse.ArgumentParser()

    #
    parser.add_argument("image", type=str, help="Image filename")
    parser.add_argument("target", type=to_tuple, help="Target pixel tuple (e.g. 0,0)")
    parser.add_argument("color", type=to_tuple, help="Color to flood fill tuple (e.g. 255,0,0)")
    # 
    parser.add_argument("--mode", type=str, default="disjointsets", help="Data structure to flood fill with")

    #
    args: Args = parser.parse_args()

    #
    makedirs("gifs", exist_ok=True)

    # Open the image
    img: Image.Image = Image.open(args.image).convert("RGB")

    #
    if args.mode == "disjointsets":
        frames = disjoint_sets_flood_fill(img, Point(*args.target), Color(*args.color))

    # 
    elif args.mode == "stack" or args.mode == "queue":
        frames = recursive_flood_fill(img, Point(*args.target), Color(*args.color), args.mode)

    # 
    frames[0].save(
        f"gifs/{Path(args.image).stem}.gif",
        save_all=True,
        append_images=frames[1:],
        duration=DURATION, 
        loop=0
    )

    
# Just calls main function
if __name__=="__main__":
    main()