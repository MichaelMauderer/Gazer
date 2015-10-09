import math
# import scipy
import pygame
import os
import gcviewer
import numpy as np
from gcviewer.interpolator import ExponentialInterpolator
from gcviewer.gcio import read_file, write_file
from gcviewer.scene import ImageStackScene
from gcviewer.engine import PyGameEngine
from gcviewer.lookup_table import HysteresisLookupTable, ArrayLookupTable
from gcviewer.image_manager import PyGameImageManager
from gcviewer import input

pygame.init()

size = width, height = 1920, 1080
dilation = 30
offset = 255 / (30 - 1)

screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

mouse_dummy = input.PygameMouseDummy()
eye_api = mouse_dummy


def make_illum_scene():
    base_path = 'C:/Users/Administrator/PycharmProjects/LFPTest/out'
    depth_array = np.load(os.path.join(base_path, 'depth_map.npy'))
    path_pattern = os.path.join(base_path, 'small/JPEG', 'img00047_f_{}.jpg')
    lut = ArrayLookupTable(depth_array)
    manager = PyGameImageManager(screen, lambda x: path_pattern.format(x))
    scene = ImageStackScene(manager, lut)
    return scene


scene = make_illum_scene()

viewer = PyGameEngine(eye_api)
viewer.display_scene(scene)

pygame.quit()
