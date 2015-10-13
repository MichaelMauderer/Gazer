import numpy as np

from gcviewer.gcio import DataDecoder
from gcviewer.scene import Scene


class HistogramEqualisationScene(Scene):
    scene_type = 'hist_color_image'

    def __init__(self, image_array, window=np.array([100, 100])):
        self._image_array = image_array
        self.window = window

    def _get_window_slice(self):
        pos_x = int(self.gaze_pos[0] * self._image_array.shape[1])
        pos_y = int(self.gaze_pos[1] * self._image_array.shape[0])

        left = pos_x - (self.window[1] // 2)
        left = np.clip(left, 0, self._image_array.shape[1])
        right = pos_x + (self.window[1] // 2)
        right = np.clip(right, 0, self._image_array.shape[1])

        top = pos_y + (self.window[0] // 2)
        top = np.clip(top, 0, self._image_array.shape[0])
        bottom = pos_y - (self.window[0] // 2)
        bottom = np.clip(bottom, 0, self._image_array.shape[0])

        image_slice = self._image_array[bottom:top, left:right]
        return image_slice

    def _get_window_equalised_image(self):
        image_slice = self._get_window_slice()
        slice_histogram, slice_bins = np.histogram(image_slice.flatten(),
                                                   256,
                                                   normed=True)
        full_histogram, full_bins = np.histogram(self._image_array.flatten(),
                                                 256,
                                                 normed=True)
        cdf = slice_histogram.cumsum()
        cdf = 255 * cdf / cdf[-1]

        equalised = np.interp(self._image_array.flatten(), full_bins[:-1], cdf)
        return equalised.reshape(self._image_array.shape)

    def get_image(self):
        # return self.histeq(self._image_array)
        return self._get_window_equalised_image()


class SimpleArrayDecoder(DataDecoder):
    """
    Naive implementation of a decoder for an ImageStackScene object.
    """

    def scene_from_data(self, data):
        import skimage.data
        image = skimage.data.imread(data)
        return HistogramEqualisationScene(image)

    def scene_from_array(self, array):
        return HistogramEqualisationScene(array)
