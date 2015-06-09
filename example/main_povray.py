import math
import pygame
import os
import gcviewer
from gcviewer.interpolator import ExponentialInterpolator
from gcviewer.scene import ImageStackScene
from gcviewer.engine import PyGameEngine
from gcviewer.lookup_table import HysteresisLookupTable, ImageLookupTable
from gcviewer.image_manager import PyGameImageManager
from gcviewer import input
from gcviewer.io import SimpleImageStack

pygame.init()

size = width, height = 1920, 1024
dilation = 30
offset = 255 / (30 - 1)

screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

mouse_dummy = input.PygameMouseDummy()
eye_api = mouse_dummy

def _get_scene(name):
    path_pattern = os.path.abspath('./resources/{0}_scene/{0}'.format(name) + '{0:0>3}.bmp')

    def depth_to_index(depth):
        return math.floor(abs(depth - 255) / offset) + 1

    def depth_to_image_path(depth):
        return path_pattern.format(depth_to_index(depth))

    # depth_map = HysteresisLookupTable(
    #     [os.path.abspath('./resources/{0}_scene/depth_maps/dilate{1}/finalMap{2}.png').format(name, dilation, i + 1) for i in range(30)],
    #     depth_to_index)
    depth_map = ImageLookupTable(os.path.abspath('./resources/{0}_scene/depth_maps/dilate{1}/finalMap{2}.png').format(name, dilation, 15))

    image_manager = PyGameImageManager(screen, depth_to_image_path)
    image_manager.preload([i + 1 for i in range(30)])

    return ImageStackScene(image_manager, depth_map)


def get_kitchen_scene():
    return _get_scene('kitchen')


def get_patio_scene():
    return _get_scene('patio')


scene = get_kitchen_scene()

with open('example_image.gc', 'wb') as out_file:
    data = SimpleImageStack.data_from_scene(scene)
    out_file.write(data)


viewer = PyGameEngine(eye_api)
viewer.display_scene(scene)

pygame.quit()