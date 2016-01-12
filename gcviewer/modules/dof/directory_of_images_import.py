"""
This module provides functionality to import a set of images from
the file system.
"""

import math
import glob
import numpy as np
import os

import skimage
from scipy import misc

from gcviewer.modules.dof.dof_data import DOFData
from gcviewer.modules.dof.scenes import ImageStackScene


def depth_to_index(depth):
    offset = 255 / (30 - 1)
    return int(math.floor(abs(depth - 255) / offset))


def dir_to_dof_data(dir_in):
    depth_map_img_format = "png"
    image_plane_format = "jpg"

    # load the depth image into an np.array
    depth_map_filename = "depthmap.{}".format(depth_map_img_format)
    depth_map_path = os.path.join(dir_in, depth_map_filename)
    depth_map = misc.imread(depth_map_path)

    # create an ordered list of all the image plane files in the directory
    image_pattern = os.path.join(dir_in, '{}.{}')

    # for each unique value in the depth array, load the image
    unique_depth_values = np.unique(depth_map)

    frame_mapping = {}
    for num, depth in enumerate(unique_depth_values):
        # index = depth_to_index(depth)
        # print(index)
        image_filename = image_pattern.format(str(int(depth)),
                                              image_plane_format)

        frame_mapping[depth] = skimage.io.imread(image_filename)
    print(unique_depth_values, frame_mapping)

    return DOFData(depth_map, frame_mapping)


def dir_to_scene(dir_in):
    dof_data = dir_to_dof_data(dir_in)
    return ImageStackScene.from_dof_data(dof_data)
