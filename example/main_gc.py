import math
import pygame
import os
import gcviewer
from gcviewer.interpolator import ExponentialInterpolator
from gcviewer.io import read_file, write_file
from gcviewer.scene import ImageStackScene
from gcviewer.engine import PyGameEngine
from gcviewer.lookup_table import HysteresisLookupTable
from gcviewer.image_manager import PyGameImageManager
from gcviewer import input


pygame.init()

size = width, height = 1920, 1024
dilation = 30
offset = 255 / (30 - 1)

screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

mouse_dummy = input.PygameMouseDummy()
eye_api = mouse_dummy

# with open('./example.gc') as in_file, open('./example_out.gc', 'w') as out_file:
#     scene = read_file(in_file, screen)
#     write_file(out_file, scene)

with open('./example_image.gc', 'r') as in_file:
     scene = read_file(in_file, screen)

viewer = PyGameEngine(eye_api)
viewer.display_scene(scene)

pygame.quit()