from __future__ import unicode_literals, division, print_function

"""
This module provides functionality to import a set of images from
the file system.
"""

import os
import logging

import numpy as np
from scipy import misc

from gcviewer.modules.dof.dof_data import DOFData
from gcviewer.modules.dof.scenes import ImageStackScene

logger = logging.getLogger(__name__)


def dir_to_dof_data(dir_in):
    depth_map_img_format = "png"
    image_plane_format = "jpg"

    # load the depth image into an np.array
    depth_map_filename = "depthmap.{}".format(depth_map_img_format)
    depth_map_path = os.path.join(dir_in, depth_map_filename)
    depth_map = misc.imread(depth_map_path)

    # for each unique value in the depth array, load the image
    unique_depth_values = np.unique(depth_map)

    image_pattern = os.path.join(dir_in, '{}.{}')
    frame_mapping = {}
    for num, depth in enumerate(unique_depth_values):
        image_filename = image_pattern.format(str(int(depth)),
                                              image_plane_format)

        try:
            frame_mapping[depth] = misc.imread(image_filename)
        except IOError:
            logger.warn('Frame {} not found.'.format(image_filename))

    return DOFData(depth_map, frame_mapping)


def dir_to_scene(dir_in):
    dof_data = dir_to_dof_data(dir_in)
    return ImageStackScene.from_dof_data(dof_data)
