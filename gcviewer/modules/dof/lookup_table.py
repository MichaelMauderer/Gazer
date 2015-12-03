from __future__ import unicode_literals, division, print_function

from abc import ABCMeta
import numpy as np

import logging

logger = logging.getLogger(__name__)


class LookupTable():
    __metaclass__ = ABCMeta

    def sample_position(self, pos):
        """
        Return the key for the image that should be shown for this position.
        """
        pass


class ArrayLookupTable(LookupTable):
    def __init__(self, array):
        super(ArrayLookupTable, self).__init__()
        self.array = array

    def sample_position(self, pos):
        try:
            x = self.array.shape[0]
            y = self.array.shape[1]
            color = self.array[int(x * pos[1]), int(y * pos[0])]
            # Avoid issues with RGB images
            result = np.average(color)
            return result
        except IndexError:
            return None


class LytroLookupTable(LookupTable):
    def __init__(self, lut_dimensions, image_dimensions, depth_txt):
        super(LytroLookupTable, self).__init__()
        self._dimensions = lut_dimensions
        self._image_dimensions = image_dimensions
        values = []
        with open(depth_txt) as depth_file:
            for line in depth_file:
                value = float(line.strip())
                values.append(value)
        self._depth_data = np.array(values)
        self._depth_data = self._depth_data.reshape(self._dimensions).T

    def sample_position(self, pos):
        x = pos[0] / self._image_dimensions[0]
        y = pos[1] / self._image_dimensions[1]

        try:
            depth = self._depth_data[int(x * (self._dimensions[0] - 1)), int(
                y * (self._dimensions[1] - 1))]
            return depth
        except IndexError:
            return None
