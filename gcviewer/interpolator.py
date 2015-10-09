from __future__ import unicode_literals, division

class Interpolator(object):
    """
    A Interpolator provides stepwise interpolation between a start and a target value.
    """

    def __init__(self, start=0, target=0):
        self.current_value = start
        self.target = target

    def make_step(self):
        """
        Do one interpolation step.
        """
        pass


class SplineInterpolator(Interpolator):
    def __init__(self, start, target, steps_to_target, start_speed=0):
        Interpolator.__init__(self, start, target)
        self.steps_to_target = steps_to_target
        self.current_speed = start_speed
        # TODO Implement
        raise NotImplementedError

    def make_step(self):
        pass


class InstantInterpolator(Interpolator):
    def make_step(self):
        return self.target


class LinearInterpolator(Interpolator):
    """
    Every step will move by the specified amount towards the target.
    """
    def __init__(self, start=0, target=0, step_size=1):
        Interpolator.__init__(self, start, target)
        self.step_size = step_size

    def make_step(self):
        if self.current_value > self.target:
            self.current_value -= self.step_size
        elif self.current_value < self.target:
            self.current_value += self.step_size
        return self.current_value


class ExponentialInterpolator(Interpolator):
    """
    Every step will half the distance towards the target (using integer division).
    """
    def make_step(self):
        diff = self.target - self.current_value
        self.current_value += diff // 2
        return self.current_value