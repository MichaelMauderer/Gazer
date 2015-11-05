import os
import yaml


def write_default_config(full_path):
    default = {'calibration_path': ''}
    with open(full_path, 'w') as yaml_file:
        yaml_dump = yaml.dump(default, default_flow_style=False)
        yaml_file.write(yaml_dump)


def ensure_config_exists(dir_path, file_name):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    full_path = os.path.join(dir_path, file_name)
    if not os.path.exists(full_path):
        write_default_config(full_path)


def load_config():
    dir_path = os.path.join(os.getenv('APPDATA'), 'gcviewer')
    file_name = 'setting.yaml'
    ensure_config_exists(dir_path, file_name)
    full_path = os.path.join(dir_path, file_name)
    with open(full_path, 'r') as config_file:
        rtn = yaml.load(config_file)
        return rtn
