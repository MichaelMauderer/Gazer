from abc import ABCMeta, abstractmethod


class Scene():
    __metaclass__ = ABCMeta

    def __init__(self):
        self.gaze_pos = None

    @abstractmethod
    def update_gaze(self, pos):
        pass

    @abstractmethod
    def render(self):
        pass

    def update_gaze(self, pos):
        self.gaze_pos = pos


class ImageStackScene(Scene):
    def __init__(self, image_manager, depth_map, interpolator):
        self.image_manager = image_manager
        self.depth_map = depth_map
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
        sampled_depth = self.depth_map.sample_position(self.gaze_pos)
        if sampled_depth is not None:
            self.interpolator.target = sampled_depth
        self.current_depth = self.interpolator.make_step()
        self.image_manager.draw_image(self.current_depth)
