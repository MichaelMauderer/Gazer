import os
import yaml


def path_to_settings_file():
    dir_path = os.path.join(os.getenv('APPDATA'), 'gcviewer')
    file_name = 'preferences.yaml'
    full_path = os.path.join(dir_path, file_name)
    return full_path


def save_preferences(full_path, prefs):
    with open(full_path, 'w') as yaml_file:
        yaml_dump = yaml.dump(prefs, default_flow_style=False)
        yaml_file.write(yaml_dump)


def write_default_preferences(full_path):
    default = {'calibration_path': ''}
    save_preferences(full_path, default)


def ensure_preferences_exists(dir_path, file_name):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    full_path = os.path.join(dir_path, file_name)
    if not os.path.exists(full_path):
        write_default_preferences(full_path)


def load_preferences():
    dir_path = os.path.join(os.getenv('APPDATA'), 'gcviewer')
    file_name = 'preferences.yaml'
    ensure_preferences_exists(dir_path, file_name)
    full_path = os.path.join(dir_path, file_name)
    with open(full_path, 'r') as config_file:
        rtn = yaml.load(config_file)
        return rtn


def get_calibration_path():
    prefs = load_preferences()
    return prefs['calibration_path']


def set_calibration_path(path):
    prefs = load_preferences()
    prefs['calibration_path'] = path
    save_preferences(path_to_settings_file(), prefs)
