from __future__ import unicode_literals, division, print_function

import numpy as np
import skimage.exposure
import skimage.data

import colour
from gcviewer.gcio import DataDecoder
from gcviewer.scene import Scene


class ArrayProcessingScene(Scene):
    def __init__(self, image_array, window=np.array([500, 500])):
        super(ArrayProcessingScene, self).__init__()
        self.image_array = image_array
        self.window = window

        xyz = colour.sRGB_to_XYZ(self.image_array / 255.)
        self._lab_array = colour.XYZ_to_Lab(xyz)

        self.image_processors = []

    def _get_array_window(self, image):
        pos_x = int(self.gaze_pos[0] * image.shape[1])
        pos_y = int(self.gaze_pos[1] * image.shape[0])

        left = pos_x - (self.window[1] // 2)
        left = np.clip(left, 0, image.shape[1])
        right = pos_x + (self.window[1] // 2)
        right = np.clip(right, 0, image.shape[1])

        top = pos_y + (self.window[0] // 2)
        top = np.clip(top, 0, image.shape[0])
        bottom = pos_y - (self.window[0] // 2)
        bottom = np.clip(bottom, 0, image.shape[0])

        image_slice = image[bottom:top, left:right]
        return image_slice

    def _get_window_mask(self):
        pos_x = int(self.gaze_pos[0] * self.image_array.shape[1])
        pos_y = int(self.gaze_pos[1] * self.image_array.shape[0])

        left = pos_x - (self.window[1] // 2)
        left = np.clip(left, 0, self.image_array.shape[1])
        right = pos_x + (self.window[1] // 2)
        right = np.clip(right, 0, self.image_array.shape[1])

        top = pos_y + (self.window[0] // 2)
        top = np.clip(top, 0, self.image_array.shape[0])
        bottom = pos_y - (self.window[0] // 2)
        bottom = np.clip(bottom, 0, self.image_array.shape[0])

        mask = np.full(self.image_array.shape[:-1], False, dtype=np.bool)
        mask[bottom:top, left:right] = True

        return mask


class HistogramEqualisationScene(ArrayProcessingScene):
    scene_type = 'hist_color_image'

    def get_image(self):
        mask = self._get_window_mask()
        out_image = skimage.exposure.equalize_hist(self.image_array,
                                                   mask=mask)

        return out_image * 255


class RescaledScene(ArrayProcessingScene):
    def get_image(self):
        if self.gaze_pos is None:
            return self.image_array
        l = self._lab_array[..., 0]
        a = self._lab_array[..., 1]
        b = self._lab_array[..., 2]

        mask = self._get_window_mask()
        window_intensities = l[mask]

        in_range = tuple(np.percentile(window_intensities, [10, 90]))
        out_range = 0, 100

        rescaled_l = skimage.exposure.rescale_intensity(l,
                                                        in_range=in_range,
                                                        out_range=out_range
                                                        )

        lab = colour.tstack([rescaled_l, a, b])

        xyz = colour.Lab_to_XYZ(lab)
        rgb = colour.XYZ_to_sRGB(xyz)

        return np.clip(rgb, 0, 1) * 255


class SimpleArrayDecoder(DataDecoder):
    """
    Naive implementation of a decoder for an ImageStackScene object.
    """

    def scene_from_data(self, data):
        image = skimage.data.imread(data)
        return HistogramEqualisationScene(image)

    def scene_from_array(self, array):
        return RescaledScene(array)
