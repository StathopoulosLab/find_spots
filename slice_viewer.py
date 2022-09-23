# slice_viewer.py

import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt

def process_key(event):
    fig = event.canvas.figure
    ax = fig.axes[0]
    if event.key == 'j':
        previous_slice(ax)
    elif event.key == 'k':
        next_slice(ax)
    fig.canvas.draw()

def process_scroll(event):
    fig = event.canvas.figure
    ax = fig.axes[0]
    step = int(event.step)
    if step != 0:
        change_slice(ax, step)
    fig.canvas.draw()

def change_slice(ax, step):
    volume = ax.volume
    ax.index = max(0, min(volume.shape[0]-1, ax.index + step))
    ax.images[0].set_array(volume[ax.index])

def previous_slice(ax):
    change_slice(ax, -1)

def next_slice(ax):
    change_slice(ax, 1)

def remove_keymap_conflicts(new_keys_set):
    for prop in plt.rcParams:
        if prop.startswith('keymap.'):
            keys = plt.rcParams[prop]
            remove_list = set(keys) & new_keys_set
            for key in remove_list:
                keys.remove(key)

def multi_slice_viewer(volume):
    remove_keymap_conflicts({'j', 'k'})
    fig, ax = plt.subplots()
    ax.volume = volume
    ax.index = volume.shape[0] // 2
    ax.imshow(volume[ax.index], cmap=cm.Greys)
    fig.canvas.mpl_connect('key_press_event', process_key)
    fig.canvas.mpl_connect('scroll_event', process_scroll)
