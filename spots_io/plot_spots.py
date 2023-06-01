# plot_spots.py

import numpy as np
import tifffile as tiff
from typing import Callable, List, Tuple, Union

def plot_spots_2D(image: np.ndarray, positions: list, scale: Union[Tuple, List], colorLambda: Callable) -> None:
    """
    colorLambda should return a color given the position
    """
    for position in positions:
        x = round(position[0] / scale[0])
        y = round(position[1] / scale[1])
        z = round(position[2] / scale[2])
        color = colorLambda(position)
        for dx in range(-6,7):
            if x + dx < 0 or x + dx >= image.shape[0]:
                continue
            for dy in range(-6, 7):
                if y + dy < 0 or y + dy >= image.shape[1]:
                    continue
                image[x+dx][y+dy] = color

def plot_spots_3D(image: np.ndarray, positions: list, scale: Union[Tuple, List], colorLambda: Callable) -> None:
    """
    colorLambda should return a color given the position
    """
    for position in positions:
        x = round(position[0] / scale[0])
        y = round(position[1] / scale[1])
        z = round(position[2] / scale[2])
        color = colorLambda(position)
        for dx in range(-6,7):
            if x + dx < 0 or x + dx >= image.shape[1]:
                continue
            for dy in range(-6, 7):
                if y + dy < 0 or y + dy >= image.shape[2]:
                    continue
                for dz in range(-1, 2):
                    if z + dz < 0 or z + dz >= image.shape[0]:
                        continue
                    image[z+dz][x+dx][y+dy] = color

