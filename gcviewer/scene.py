from abc import ABCMeta, abstractmethod
from gcviewer.interpolator import InstantInterpolator


class Scene():
    __metaclass__ = ABCMeta

    def __init__(self):
        self.gaze_pos = None

    def update_gaze(self, pos):
        self.gaze_pos = pos

    @abstractmethod
    def render(self):
        pass


class ImageStackScene(Scene):
    def __init__(self, image_manager, lookup_table, interpolator=InstantInterpolator()):
        self.image_manager = image_manager
        self.lookup_table = lookup_table
        self.interpolator = interpolator

        self.current_depth = 0
        self.target_depth = 0
        self.gaze_pos = None

        self.p = False

    def set_depth(self, depth):
        self.target_depth = depth

    def render(self):
        if not self.gaze_pos:
            return
        sampled_depth = self.lookup_table.sample_position(self.gaze_pos)
        if sampled_depth is not None:
            self.interpolator.target = sampled_depth
        self.current_depth = self.interpolator.make_step()
        self.image_manager.draw_image(self.current_depth)
