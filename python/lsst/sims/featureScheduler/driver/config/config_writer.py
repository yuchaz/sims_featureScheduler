import configparser
import os
import json

config = configparser.SafeConfigParser()
current_dir = os.path.dirname(os.path.abspath(__file__))
default_config = os.path.join(current_dir,'default.cfg')
updated_config = os.path.join(current_dir,'updated.cfg')

def write_config(weights=None, config_file=default_config):
    if weights is None:
        weights = [3.0, 0.5, 1., 3., 3., 3.]
    if not config.has_section("basis_function"):
        config.add_section("basis_function")
    config.set("basis_function", "weights", json.dumps(weights))
    with open(config_file, 'w') as configfile:
        config.write(configfile)

def get_config(section, option, iflist=False, config_file=None):
    if config_file is None:
        config_file = updated_config if os.path.exists(updated_config) else default_config

    config.read(config_file)
    result = config.get(section, option)
    return json.loads(result) if iflist else result

if __name__ == '__main__':
    write_config()
