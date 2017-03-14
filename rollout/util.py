from pathlib import Path
import yaml


def load_config(path):
    return yaml.load(open(path))


def discover_config(config_name):
    check_dir = Path.cwd()

    while check_dir != check_dir.parent:

        path = check_dir.joinpath(config_name)
        if path.exists():
            return load_config(path)
        check_dir = check_dir.parent
