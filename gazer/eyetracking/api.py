from __future__ import unicode_literals, division, print_function

import collections
import logging

logger = logging.getLogger(__name__)

EyeData = collections.namedtuple('EyeData',
                                 ['timestamp',
                                  'pos',
                                  ])


class TrackerUnavailableError(RuntimeError):
    pass


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
    """
    Detects and returns the available eye tracking apis.

    Returns
    -------
    Dict of name:api for all available eye tracking apis.

    """
    apis = {}
    try:
        from gazer.eyetracking.tobii import EyeXWrapper
        eye_x = EyeXWrapper()
        apis['eyex'] = eye_x
    except RuntimeError:
        logger.exception('Could not load EyeX api.')

    return apis
