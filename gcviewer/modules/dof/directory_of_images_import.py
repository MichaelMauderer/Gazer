"""
This module provides functionality to import a set of images from
the file system.
"""

import math
import glob
import numpy as np
import os

from scipy import misc


def depth_to_index(depth):
    offset = 255 / (30 - 1)
    return int(math.floor(abs(depth - 255) / offset))


def dir_to_dof_data(dir_in):
    depth_map_img_format = "png"
    image_plane_format = "bmp"

    # load the depth image into an np.array
    depth_map_filename = "depthmap.{}".format(depth_map_img_format)
    depth_map_path = os.path.join(dir_in, depth_map_filename)
    depth_map = misc.imread(depth_map_path)

    # create an ordered list of all the image plane files in the directory
    image_pattern = os.path.join(dir_in, '*.{}'.format(image_plane_format))
    image_filenames = sorted(glob.glob(image_pattern))
    if depth_map_path in image_filenames:
        image_filenames.remove(depth_map_path)

    # for each unique value in the depth array, load the image
    unique_depth_values = np.unique(depth_map)

    indices = [depth_to_index(depth) for depth in unique_depth_values]

    frame_mapping = []
    for num, depth in enumerate(unique_depth_values):
        index = depth_to_index(depth)
        print(index)
        # image_filename =
        # image =
        # frame_mapping[depth] =
    print(indices, frame_mapping)
