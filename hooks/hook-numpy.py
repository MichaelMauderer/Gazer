"""
Ensures numpy libraries are correctly copied from conda package.
Based on : http://stackoverflow.com/a/35853001/1175813
"""
from PyInstaller import log as logging
from PyInstaller import compat
import os

logger = logging.getLogger(__name__)

lib_dir = 'C:\\miniconda'
mkl_libs = []
logger.info('Searching for MKL libs in {}'.format(lib_dir))
for root, dirs, files in os.walk(lib_dir):
    matches = list(filter(lambda x: x.startswith('libmkl_'), files))
    mkl_libs += matches

if mkl_libs:
    logger.info("MKL libs found: {}".format(' '.join(mkl_libs)))
    binaries = map(lambda l: os.path.join(lib_dir, l), mkl_libs)
else:
    logger.warning("MKL libs not found.")
