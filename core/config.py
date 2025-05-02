from typing import Union

import configparser
import json
import os

CONFIG_FILE = 'config.ini'
DEFAULT_CONFIG = {
    'websocket': {
        'port': 9222
    },
    'app': {
        'theme': 'default-dark'
    }
}


def create_config() -> configparser.ConfigParser:
    parser = configparser.ConfigParser()

    if os.path.exists(CONFIG_FILE):
        parser.read(CONFIG_FILE)
    
    for section, data in DEFAULT_CONFIG.items():
        if section not in parser.sections():
            parser.add_section(section)
        
        for option, value in data.items():
            if not parser.has_option(section, option):
                parser.set(section, option, json.dumps(value))
    
    with open(CONFIG_FILE, 'w') as file:
        parser.write(file)
        file.close()
    return parser


def load_config() -> dict:
    parser = create_config()
    parser.read(CONFIG_FILE)
    data = dict()
    for section in parser.sections():
        data[section] = dict((option, json.loads(value)) for option, value in parser.items(section))
    return data


def load_config_value(section: str, option: str) -> Union[str, int]:
    parser = create_config()
    parser.read(CONFIG_FILE)
    return json.loads(parser.get(section, option))
