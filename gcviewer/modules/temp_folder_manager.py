import tempfile
import shutil


class TempFolderManager(object):
    def __enter__(self):
        # self.tmp_dir = tempfile.mkdtemp()
        self.tmp_dir = "../tmp" # TODO: Change this to somewhere more reasonable
        return self.tmp_dir

    def __exit__(self, ex_type, value, traceback):
        #shutil.rmtree(self.tmp_dir)
        pass
