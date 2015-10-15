from __future__ import unicode_literals, division, print_function

import logging

from gcviewer.eyetracking.api import EyetrackingAPIBase, EyeData
import pytribe

logger = logging.getLogger(__name__)


class EyeTribeWrapper(EyetrackingAPIBase, pytribe.EyeTribe):
    def __init__(self):
        EyetrackingAPIBase.__init__(self)
        pytribe.EyeTribe.__init__(self)
        self.start_recording()

    def _convert_sample(self, eyetribe_sample):
        x, y = eyetribe_sample['rawx'], eyetribe_sample['rawy']
        eye_data_sample = EyeData(eyetribe_sample['timestamp'], (x, y))
        return eye_data_sample

    def get_newest_sample(self):
        eyetribe_sample = self.sample()
        return self._convert_sample(eyetribe_sample)

    def _log_sample(self, sample):
        self._on_event(self._convert_sample(sample))
