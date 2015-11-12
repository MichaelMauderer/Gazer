from __future__ import division, print_function, unicode_literals

from collections import Counter
import json
import os
from functools import wraps
import logging
import shutil
import tempfile
from scipy import misc
import numpy as np
import yaml


from lpt.lfp.tnt import Tnt

from gcviewer.modules.dof.image_manager import ArrayStackImageManager
# from gcviewer.gcio import write_file
from gcviewer.modules.dof.lookup_table import ArrayLookupTable
from gcviewer.modules.dof.scenes import ImageStackScene


def tnt_command_sequence(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        tnt = Tnt()
        result = f(tnt, *args, **kwargs)
        tnt.execute()
        return result
    return wrapper


@tnt_command_sequence
def make_depth_map(tnt, lfp_in, depth_out_folder, depth_out_file_fame):
    file_type = 'bmp'
    out_file = '{}.{}'.format(depth_out_file_fame, file_type)
    out_path = os.path.join(depth_out_folder, out_file)

    tnt.lfp_in(lfp_in)
    tnt.depthrep(file_type)
    tnt.depth_out(out_path)
    tnt.dir_out(depth_out_folder)


def read_depth_data(depth_dir, name):
    depth_map_path = os.path.join(depth_dir, '{}.bmp'.format(name))
    depth_meta_data_path = os.path.join(depth_dir, '{}.jsn'.format(name))
    depth_map = misc.imread(depth_map_path)
    with open(depth_meta_data_path) as meta_data_file:
        depth_meta = json.load(meta_data_file)
    return depth_map, depth_meta


def get_depth_data(lfp_in):
    tmp_dir = tempfile.mkdtemp()
    depth_out_file_fame = 'depth'
    try:
        make_depth_map(lfp_in, tmp_dir, depth_out_file_fame)
        return read_depth_data(tmp_dir, depth_out_file_fame)
    finally:
        shutil.rmtree(tmp_dir)


@tnt_command_sequence
def make_focus_image(tnt, lfp_in, image_out, focus, calibration):
    tnt.calibration_in(calibration)
    tnt.lfp_in(lfp_in)
    tnt.image_out(image_out)
    tnt.focus(str(focus))


def get_main_depth_planes(depth_map, threshold=0.005):
    overall_count = depth_map.size
    counts = Counter(depth_map.flat)
    main_depth_planes = []
    for depth, depth_count in counts.iteritems():
        if depth_count > threshold * overall_count:
            main_depth_planes.append(depth)
    return main_depth_planes


def depth_value_to_lambda(pixel_value, pixel_value_max, lambda_min, lambda_max):
    pixel_norm = pixel_value / pixel_value_max
    lambda_range = lambda_max - lambda_min
    lambda_values = (pixel_norm * lambda_range) + lambda_min
    return np.rint(lambda_values).astype(int)


def depth_map_to_index(lambda_map, focus_array):
    for x in np.nditer(lambda_map, op_flags=['readwrite']):
        x[...] = (np.abs(focus_array-x)).argmin()


def make_stack(lfp_in, calibration, out_path, verbose=False,
               skip_existing=False):
    # print(out_path)

    depth_map, depth_meta = get_depth_data(lfp_in)
    depth_planes = np.array(get_main_depth_planes(depth_map))

    focal_planes = depth_value_to_lambda(depth_planes,
                                         depth_map.max(),
                                         depth_meta['LambdaMin'],
                                         depth_meta['LambdaMax'])

    lambda_map = depth_value_to_lambda(depth_map,
                                       depth_map.max(),
                                       depth_meta['LambdaMin'],
                                       depth_meta['LambdaMax'])

    depth_map_to_index(depth_map, focal_planes)
    ## depth_map_path = os.path.join(out_path, 'depth_map.npy')
    # np.save(depth_map_path, lambda_map)

    unique_focal_planes = np.unique(focal_planes)

    file_name = os.path.basename(str(lfp_in)).split('.')[0] + '_f_{}.jpg'
    stack_images = []
    for num, focus in enumerate(unique_focal_planes):
        out_image = os.path.join(out_path, file_name.format(focus))
        stack_images.append(out_image)
        if skip_existing and os.path.exists(out_image):
            if verbose:
                print(
                    'Skipping focal plane f={} becasue {} already exists ({}/{}).'.format(
                        focus,
                        out_image,
                        num + 1,
                        unique_focal_planes.size)
                )
            continue
        if verbose:
            print('Creating focal plane f={} as {} ({}/{}).'.format(focus,
                                                                    out_image,
                                                                    num + 1,
                                                                    unique_focal_planes.size))
        make_focus_image(lfp_in, out_image, focus, calibration)
    stack_images = [misc.imread(img_path) for img_path in stack_images]
    # depth_map = np.load(depth_map_path)
    return depth_map, stack_images


def read_ifp(file_name, config):
    print('Loading IFP or IFR file: ' + file_name)

    calibration = config['calibration_path']

    verbose = True

    scene = None

    tmp_dir = tempfile.mkdtemp()
    try:
        depth_map, focus_stack_images = make_stack(file_name,
                                                   calibration,
                                                   tmp_dir,
                                                   verbose=verbose,
                                                   skip_existing=True)
        lut = ArrayLookupTable(depth_map)
        manager = ArrayStackImageManager(focus_stack_images)
        scene = ImageStackScene(manager, lut)

    except Exception as e:
        logging.error("Error loading ifp file " + file_name)
        logging.error(e)

    finally:
        shutil.rmtree(tmp_dir)

    print('Finished Loading.')

    return scene


