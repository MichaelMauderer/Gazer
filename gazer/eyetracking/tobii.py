from __future__ import unicode_literals, division, print_function

import os
import logging

from gazer.eyetracking.api import EyetrackingAPIBase, EyeData
import eyex.api

logger = logging.getLogger(__name__)


class EyeXWrapper(EyetrackingAPIBase):
    def __init__(self):
        EyetrackingAPIBase.__init__(self)
        lib_path = os.path.join(os.getenv('EYEX_LIB_PATH', ''),
                                'Tobii.EyeX.Client.dll'
                                )
        logger.info('Expecting Tobii.EyeX.Client.dll at {}'.format(lib_path))
        self._eye_x_interface = eyex.api.EyeXInterface(lib_path)
        self._eye_x_interface.on_event += [self._update_sample]

    def _update_sample(self, sample):
        self._current_sample = self._convert_sample(sample)
        self._on_event(self._current_sample)

    def _convert_sample(self, native_sample):
        x, y = native_sample.x, native_sample.y
        eye_data_sample = EyeData(native_sample.timestamp, (x, y))
        return eye_data_sample

    def get_newest_sample(self):
        return self._current_sample
