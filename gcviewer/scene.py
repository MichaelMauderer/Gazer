from __future__ import unicode_literals, division, print_function

from abc import ABCMeta, abstractmethod


class Scene():
    """
    Base class for gaze-contingent scenes that can be displayed.
    Provide frames based on current gaze state.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self.gaze_pos = None

    def update_gaze(self, pos):
        """
        Set current gaze position.

        Parameters
        ----------
        pos : tuple
            Gaze position normalized to image coordinates (0,1).
        """
        self.gaze_pos = pos

    def tick(self, delta_time):
        """
        Advance internal scene logic by specified time.

        Parameters
        ----------
        delta_time : float
            Time passed since last call.
        """
        pass

    @abstractmethod
    def get_image(self):
        """
        Return frame for current state.
        Type might depend on rendering engine used.
        """
        pass
