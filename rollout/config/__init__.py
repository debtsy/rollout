import sys
from pathlib import Path
import yaml
from collections import OrderedDict
from typing import Optional, Tuple


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):

    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)


yaml.add_representer(OrderedDict, represent_ordereddict, Dumper=yaml.SafeDumper)


def safe_load(stream):
    return ordered_load(stream, yaml.SafeLoader)


def load_file(path: Path) -> Optional[OrderedDict]:
    suffix = path.suffix
    if suffix in {'.yaml', '.yml'}:
        return safe_load(open(str(path)))
    return None


def load_directory(path: Path) -> OrderedDict:
    config = OrderedDict()
    for p in sorted(path.iterdir()):
        if p.stem in config:
            raise ValueError(f'Trying to load file {p}, but key {p.stem} already exists.')
        if p.is_dir():
            config[p.stem] = load_directory(p)
        else:
            conf = load_file(p)
            if conf is not None:
                if p.stem == 'config':
                    for k in conf:
                        if k in config:
                            raise ValueError(f'Trying to insert key {k} from file {p}, but key already exists.')
                    config.update(conf)
                else:
                    config[p.stem] = conf
    return config


def load_directory_or_file(path: Path) -> OrderedDict:
    if path.is_dir():
        return load_directory(path)
    else:
        return load_file(path)


def is_rollout_directory(path: Path) -> Optional[Path]:
    for p in [
        path / '.rollout',
        path / '.rollout.yaml',
        path / 'rollout.yaml',
    ]:
        if p.exists():
            return p
    return None


def discover_config(path: str) -> OrderedDict:
    if path is None:
        check_dir = Path.cwd()
    else:
        check_dir = Path(path)

    while check_dir != check_dir.parent:
        config_path = is_rollout_directory(check_dir)
        if config_path:
            config = load_directory_or_file(config_path)
            config['__filepath'] = config_path
            return config
        check_dir = check_dir.parent


CONFIG = None


def load_global_config():
    global CONFIG
    if CONFIG is None:
        CONFIG = load_directory_or_file(Path('~/.rollout_global').expanduser())
    return CONFIG


def get_global(key, default=None):
    keys = key.split('.')
    d = CONFIG
    for k in keys:
        d = d.get(k)
        if d is None:
            return default
    return d


def display(args, config):
    yaml.safe_dump(config, sys.stdout, indent=4)
