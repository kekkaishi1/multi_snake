#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
test module
"""

__author__ = 'Lin Xin'

import sys
import json


def open_config():
    config_file = '{}\\config\\default.json'.format(sys.path[0])
    with open(config_file) as f:
        config = json.load(f)
    return config


def get_config():
    config = open_config()
    game_config = config['game_config']
    return game_config


def get_resource():
    config = open_config()
    resources = config['resources']
    return resources


def get_settings():
    config = open_config()
    settings = config['game_settings']
    return settings


def set_config():
    pass


def main():
    print("This is config file, please import this module to load config")


if __name__ == '__main__':
    main()
