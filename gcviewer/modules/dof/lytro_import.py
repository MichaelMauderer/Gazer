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

from gcviewer.modules.temp_folder_manager import TempFolderManager
from gcviewer.modules.dof.dof_data import DOFData
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
    # depth_map = depth_map[..., ..., 0] # TODO: Reduce depth map to one value per pixel
    with open(depth_meta_data_path) as meta_data_file:
        depth_meta = json.load(meta_data_file)
    return depth_map, depth_meta


def get_depth_data(lfp_in):
    with TempFolderManager() as tmp_dir:
        depth_out_file_fame = 'depth'
        make_depth_map(lfp_in, tmp_dir, depth_out_file_fame)
        return read_depth_data(tmp_dir, depth_out_file_fame)


@tnt_command_sequence
def make_focus_image(tnt, lfp_in, image_out, focus, calibration):
    tnt.calibration_in(calibration)
    tnt.lfp_in(lfp_in)
    tnt.image_out(image_out)
    tnt.width(256)
    tnt.height(256)
    tnt.focus(str(focus))


def get_main_depth_planes(depth_map, threshold=0.02):
    overall_count = depth_map.size
    counts = Counter(depth_map.flat)
    main_depth_planes = []
    for depth, depth_count in counts.iteritems():
        if depth_count > threshold * overall_count:
            main_depth_planes.append(depth)
    return main_depth_planes


def remap(value, from_range, to_range):
    from_start, from_end = from_range
    assert np.all(from_start <= value <= from_end), \
        "Value {} not between {}, {}".format(value, from_start, from_end)
    from_range_len = from_end - from_start
    normalized_value = (value - from_start) / from_range_len
    to_start, to_end = to_range
    assert to_start < to_end
    to_range_len = to_end - to_start
    remapped_value = (normalized_value * to_range_len) + to_start
    return remapped_value


def value_map_to_index_map(value_map, index_list):
    """
    Return every value in the value_map with the index of the closest value from the index_list.

    Parameters
    ----------
    value_map : ndarray
    index_list : list
    """
    index_array = np.array(index_list)

    def indexify(val):
        dist = index_array - val
        abs_dist = np.abs(dist)
        return abs_dist.argmin()

    result = [indexify(x) for x in value_map.flat]
    result = np.array(result).reshape(value_map.shape)
    return result


def ifp_to_dof_data(lfp_in, calibration, out_path, verbose=False):
    depth_map, depth_meta = get_depth_data(lfp_in)
    depth_range = depth_map.min(), depth_map.max()
    lambda_range = depth_meta['LambdaMin'], depth_meta['LambdaMax']

    def remap_lambda(value):
        return remap(value, depth_range, lambda_range)

    frame_mapping = {}
    file_name_template = os.path.basename(str(lfp_in)).split('.')[0] + '_f_{}.jpg'
    unique_depth_values = np.unique(depth_map)
    for num, depth in enumerate(unique_depth_values):
        lambda_value = remap_lambda(depth)
        out_image = os.path.join(out_path, file_name_template.format(lambda_value))
        logging.debug("Processing image {} - {}/{}".format(out_image, num, len(unique_depth_values)))
        if not os.path.exists(out_image):
            make_focus_image(lfp_in, out_image, lambda_value, calibration)
        if depth not in frame_mapping:
            image = misc.imread(out_image)
            frame_mapping[depth] = image

    return DOFData(depth_map, frame_mapping)


def read_ifp(file_name, config):
    print('Loading IFP or IFR file: ' + file_name)

    calibration = config['calibration_path']

    verbose = True

    scene = None

    with TempFolderManager() as tmp_dir:
        try:
            dof_data = ifp_to_dof_data(file_name, calibration, tmp_dir, verbose)
            scene = ImageStackScene.from_dof_data(dof_data)

        except Exception:
            logging.exception("Error loading ifp file " + file_name)

    print('Finished Loading.')

    return scene


