from __future__ import unicode_literals, division, print_function

from abc import ABCMeta, abstractmethod
import collections

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
