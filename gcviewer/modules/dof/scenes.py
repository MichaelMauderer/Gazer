from __future__ import unicode_literals, division, print_function

import io
import bson
from bson import BSON
import numpy as np
from gcviewer.gcio import DataDecoder, array_to_bytes, bytes_to_array, \
    DataEncoder
from gcviewer.modules.dof.image_manager import ArrayStackImageManager
from gcviewer.modules.dof.interpolator import LinearInterpolator
from gcviewer.modules.dof.lookup_table import ArrayLookupTable
from gcviewer.scene import Scene


class ImageStackScene(Scene):
    """
    Scene object based on a list of images and a depth map.

    The current image to be displayed is chosen based on correspondence between
    the value in the depth map at the gaze position and the index position in
    the image array.

    Todo: More detail about algorithm, e.g. interpolation.
    """
    scene_type = 'simple_array_stack'

    def __init__(self, image_manager, lookup_table,
                 interpolator=LinearInterpolator()):
        self.image_manager = image_manager
        self.lookup_table = lookup_table
        self.interpolator = interpolator

        self._current_depth = 0
        self.target_depth = 0
        self.gaze_pos = None

        self.p = False

    def set_depth(self, depth):
        self.target_depth = depth

    @property
    def current_depth(self):
        if not self.gaze_pos:
            return
        sampled_depth = self.lookup_table.sample_position(self.gaze_pos)
        if sampled_depth is not None:
            self.interpolator.target = sampled_depth
        self._current_depth = self.interpolator.make_step()
        return self._current_depth

    def render(self):
        self.image_manager.draw_image(self.current_depth)

    def get_image(self):
        return self.image_manager.load_image(self.current_depth)

    def get_depth_image(self):
        array = self.lookup_table.array
        max_elem = array.max()
        min_elem = array.min()
        array_normalised = 255 * ((array - min_elem) / (max_elem - min_elem))

        return np.asarray(array_normalised, np.uint8)


class SimpleArrayStackDecoder(DataDecoder):
    """
    Naive implementation of a decoder for an ImageStackScene object.
    """

    def scene_from_data(self, data):
        bson_data = BSON(data)
        data_dict = bson_data.decode()
        decoded_array = self._decode_array(data_dict[u'lookup_table'])
        lut = ArrayLookupTable(decoded_array)
        frames = [self._decode_array(value) for key, value
                  in
                  sorted(data_dict['frames'].items(), key=lambda x: int(x[0]))]
        image_manager = ArrayStackImageManager(frames)
        scene = ImageStackScene(image_manager, lut)
        return scene

    def _decode_array(self, data):
        array = bytes_to_array(data)
        array.flags.writeable = False
        return array


class SimpleArrayStackEncoder(DataEncoder):
    """
    Naive implementation of a encoder for an ImageStackScene object.
    """

    def data_from_scene(self, scene):
        lut_array = scene.lookup_table.array

        def frame_iterator():
            for frame_index in sorted(scene.image_manager.keys):
                frame = scene.image_manager.load_array(frame_index)
                yield frame

        stream = io.BytesIO()

        frames = {str(key): self._encode_array(array) for key, array in
                  enumerate(frame_iterator())}

        data = {'lookup_table': self._encode_array(lut_array),
                'frames': frames
                }

        stream.write(BSON.encode(data))
        stream.seek(0)
        return bson.Binary(stream.getvalue())

    def _encode_array(self, array):
        bytes_str = array_to_bytes(array)
        return bson.Binary(bytes_str)
