import scipy.misc
import os
import numpy as np

from gcviewer.image_manager import ArrayStackImageManager


from gcviewer.io import array_to_bytes, SimpleImageStack, write_file
from gcviewer.lookup_table import ImageLookupTable, ArrayLookupTable
from gcviewer.scene import ImageStackScene

if __name__ == '__main__':
    base_path = 'C:/Users/Administrator/PycharmProjects/LFPTest/out'
    depth_array = np.load(os.path.join(base_path, 'depth_map.npy'))
    print(depth_array.shape)
    #path_pattern = os.path.join(base_path,'small/JPEG', 'img00047_f_{}.jpg')
    path_pattern = os.path.join(base_path,  'img00047_f_{}.jpg')
    frames = []
    for index in range(120):
        img_path = path_pattern.format(index)
        if os.path.exists(img_path):
            array = scipy.misc.imread(img_path)
            frames.append(array)
    lut = ArrayLookupTable(depth_array)
    manager = ArrayStackImageManager(frames)
    scene = ImageStackScene(manager, lut)

    with open('example_lytro_image.gc', 'w') as out_file:
        write_file(out_file, scene)