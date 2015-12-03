class DOFData(object):
    def __init__(self, depth_array, frame_mapping):
        """
        :param depth_array: 2D numpy array with values in range 0-255
        :param frame_mapping: Dictionary mapping values in depth_array to images
        """
        self.depth_array = depth_array
        self.frame_mapping = frame_mapping
