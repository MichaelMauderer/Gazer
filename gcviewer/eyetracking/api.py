from __future__ import unicode_literals, division, print_function

import os
import collections
import logging

from abc import ABCMeta, abstractmethod


logger = logging.getLogger(__name__)

EyeData = collections.namedtuple('EyeData',
                                 ['timestamp',
                                  'pos',
                                  'norm_pos',
                                  ])


class EyetrackingAPIBase:
    """
    Base class for eye tracking data sources.
    Specifies common functionality that needs to be supplied.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def pop_sample(self):
        """
        Returns oldest available EyeData sample.
        """
        return NotImplemented

    @abstractmethod
    def pop_all_samples(self):
        """
        Returns all available EyeData samples.
        """
        return NotImplemented

    @abstractmethod
    def get_newest_sample(self):
        """
        Returns newest available EyeData sample.
        """
        pass


def get_available():
    apis = {}
    try:
        import eyex
        lib_path = os.path.join(os.getenv('EYEX_LIB_PATH', ''),
                                'Tobii.EyeX.Client.dll')
        eye_x = eyex.api.EyeXInterface(lib_path)
        apis['eyex'] = eye_x
    except:
        logger.warn('Could not load EyeX api.')

    if not apis:
        logger.warn('No valid eye tracking apis could be loaded')

    return apis
