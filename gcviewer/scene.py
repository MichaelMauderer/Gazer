from abc import ABCMeta, abstractmethod
from gcviewer.interpolator import InstantInterpolator, LinearInterpolator


class Scene():
    __metaclass__ = ABCMeta

    def __init__(self):
        self.gaze_pos = None

    def update_gaze(self, pos):
        """
        :param pos: Gaze position normalized to image.
        """
        self.gaze_pos = pos

    @abstractmethod
    def render(self):
        pass


class ImageStackScene(Scene):
    def __init__(self, image_manager, lookup_table, interpolator=LinearInterpolator()):
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
