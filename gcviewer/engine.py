class GCViewer():
    def __init__(self, input_api):
        self.input_api = input_api
        self.scene = None

    def update_scene(self):
        if self.scene is None:
            return
        sample = self.input_api.get_newest_sample()
        if sample is None or sample.pos is None:
            return
        self.scene.update_gaze(sample.pos)

    def run(self):
        while not self.handle_input():
            self.update_scene()
            self.scene.render()

    def display_scene(self, scene):
        self.scene = scene
        self.run()

    def handle_input(self):
        return False

import pygame
class PyGameEngine(GCViewer):
    def handle_input(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYUP and event.key == 27:
                return True
