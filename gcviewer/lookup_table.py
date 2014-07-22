from __future__ import division
from abc import ABCMeta
import numpy as np
from scipy import ndimage
import scipy


class LookupTable():
    __metaclass__ = ABCMeta

    def sample_position(self, pos):
        """
        Return the key for the image that should be shown for this position.
        """
        pass


class ArrayLookupTable(LookupTable):
    def __init__(self, array):
        super().__init__()
        self.array = array

    def sample_position(self, pos):
        try:
            color = self.array[pos[1], pos[0]]
            result = np.average(color)
            return result
        except IndexError:
            return None


class ImageLookupTable(ArrayLookupTable):
    def __init__(self, path):
        super().__init__(scipy.misc.imread(path))


class FilteredImageLookupTable(ImageLookupTable):
    def __init__(self, path, filter_function):
        super().__init__(path)
        self.array = filter_function(self.array)


class ErodedImageLookupTable(ImageLookupTable):
    def __init__(self, path, kernel):
        super().__init__(path)
        self.erode_map(kernel)

    def erode_map(self, kernel):
        self.array = ndimage.grey_erosion(self.array, kernel)


class HysteresisLookupTable(LookupTable):
    def __init__(self, path_list, depth_to_index=lambda x: x, initial_index=0):
        self._depthmaps = [scipy.misc.imread(path) for path in path_list]
        self.depth_to_index = depth_to_index
        self._current_index = initial_index

    def sample_position(self, pos):
        depthmap = self._depthmaps[self._current_index]
        try:
            color = depthmap[pos[1], pos[0]]
            depth = np.average(color)
            self._current_index = self.depth_to_index(depth)
            return depth
        except IndexError:
            return None


class LytroLookupTable(LookupTable):
    def __init__(self, lut_dimensions, image_dimensions, depth_txt):
        super().__init__()
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
            depth = self._depth_data[int(x * (self._dimensions[0] - 1)), int(y * (self._dimensions[1] - 1))]
            return depth
        except IndexError:
            return None


class PerspectiveCorrectedLookupTable(ImageLookupTable):
    def __init__(self, path, fov):
        super().__init__(path)
        self.fov = fov
        self.array = self.correct_depth_map(self.array, self.fov)

    @staticmethod
    def correct_depth_map(uncorrected_depthmap, fov, normalise=False):
        """
        Returns depthmap that contains distances to scene plane.

        Parameters
        ----------
        depth_map : Depth map with distances to camera
        fov : Angle of field of view (longest edge of the given scene) in radians.
        """
        depth_map = uncorrected_depthmap

        x_offset = depth_map.shape[0] / 2
        y_offset = depth_map.shape[1] / 2
        max_side = max(depth_map.shape)

        y, x = np.indices(depth_map.shape)

        center_deviation = np.sqrt((y - y_offset) ** 2 + (x - x_offset) ** 2)
        center_deviation /= max_side / 2

        alpha = center_deviation * np.sin(fov / 2) / np.sin(np.pi / 2 - fov / 2)
        alpha = np.arctan(alpha)

        depth_map *= np.sin((np.pi / 2) - alpha)

        if normalise:
            maximum = np.max(depth_map)
            minimum = np.min(depth_map)
            depth_map -= minimum
            depth_map *= 255 / (maximum - minimum)

        return depth_map
