#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
test module
"""

__author__ = 'Lin Xin'

import sys
import json



def get_config():
    config_file='{}\\config\\default.json'.format(sys.path[0])
    with open(config_file) as f:
        config = json.load(f)
    config[]

def set_config():
    pass


def main():
    return


if __name__ == '__main__':
    main()
    
