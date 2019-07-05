from os import mkdir
from os.path import exists, expanduser, join
import ConfigParser

_config = None
_config_root = expanduser('~/.config/acfun-joker')
_download_root = expanduser('~/Downloads/acfun-joker')

exists(_config_root) or mkdir(_config_root)
exists(_download_root) or mkdir(_download_root)

_config_file = join(_config_root, 'config')
_db_file = join(_config_root, 'entity.sqlite3')


def _load_config():
    global _config

    if _config is None:
        config = ConfigParser.ConfigParser()

        if exists(_config_file):
            config.read(_config_file)
        else:
            config.add_section('DATABASE')
            config.set('DATABASE', 'path', _db_file)

            config.add_section('DOWNLOAD')
            config.set('DOWNLOAD', 'you-get', '')
            config.set('DOWNLOAD', 'path', _download_root)

            with open(_config_file, 'wb') as f:
                config.write(f)

    return config


def get_db_path():
    config = _load_config()
    return config.get('DATABASE', 'path')

def get_download_path():
    config = _load_config()
    return config.get('DOWNLOAD', 'path')

def get_download_options():
    config = _load_config()
    return config.get('DOWNLOAD', 'you-get')
