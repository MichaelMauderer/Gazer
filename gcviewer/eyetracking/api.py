from __future__ import unicode_literals, division, print_function

import os
import collections
import logging


logger = logging.getLogger(__name__)

EyeData = collections.namedtuple('EyeData',
                                 ['timestamp',
                                  'pos',
                                  ])


class EyetrackingAPIBase(object):
    """
    Base class for eye tracking data sources.
    Specifies common functionality that needs to be supplied.
    """

    def __init__(self):
        self.on_event = []

    def _on_event(self, event):
        for cb in self.on_event:
            cb(event)

    def get_newest_sample(self):
        """
        Returns newest available EyeData sample.
        """
        pass


def get_available():
    apis = {}
    try:
        from gcviewer.eyetracking.tobii import EyeXWrapper
        eye_x = EyeXWrapper()
        apis['eyex'] = eye_x
    except:
        logger.exception('Could not load EyeX api.')

    try:
        from gcviewer.eyetracking.eyetribe import EyeTribeWrapper
        apis['eyetribe'] = EyeTribeWrapper()
    except:
        logger.exception('Could not load Eyetribe api.')

    if not apis:
        logger.warn('No valid eye tracking apis could be loaded')

    return apis
