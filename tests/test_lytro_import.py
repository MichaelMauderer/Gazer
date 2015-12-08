import numpy as np
from gcviewer.modules.dof.lytro_import import value_map_to_index_map, remap


def test_value_map_to_index_map():
    index_list = [21, 22, 24, 128]
    value_map = np.array(
            [
                [21, 22, 24, 128],
                [21, 22, 24, 128],
                [21, 22, 24, 128],
                [21, 22, 24, 128],
            ]
    )
    index_map = value_map_to_index_map(value_map, index_list)
    expected = np.array(
            [
                [0, 1, 2, 3],
                [0, 1, 2, 3],
                [0, 1, 2, 3],
                [0, 1, 2, 3],
            ]
    )
    np.testing.assert_array_equal(index_map, expected)


def test_value_map_to_index_map_simple():
    index_list = [0, 255]
    value_map = np.array(
            [
                [0, 123],
                [234, 255]
            ]
    )
    index_map = value_map_to_index_map(value_map, index_list)
    expected = np.array(
            [
                [0, 0],
                [1, 1],
            ]
    )
    np.testing.assert_array_equal(index_map, expected)


def test_remap():
    np.testing.assert_allclose(remap(0.5, (0, 1), (10, 20)), [15])
    np.testing.assert_allclose(remap(0.5, (0, 1), (-10, 10)), [0])
    np.testing.assert_allclose(remap(0.5, (-1, 1), (10, 20)), [17.5])
