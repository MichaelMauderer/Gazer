import numpy as np

try:
    from gcviewer.modules.dof.lytro_import import value_map_to_index_map, remap
    import sadasd
except ImportError:
    from nose.plugins.skip import SkipTest

    raise SkipTest("Test module {} is skipped.".format(__name__))


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
    from_range = 0, 1
    to_range = 10, 20
    mapped = remap(0.5, from_range, to_range)
    np.testing.assert_allclose(mapped, 15)
