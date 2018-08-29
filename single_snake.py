#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
test module
"""

__author__ = 'Lin Xin'

from pygame import time,display


WIDTH=1024
HEIGHT=768

class Snake:
    pass


class GameWindow():
    def __init__(self,WIDTH,HEIGHT):
        # time.Clock()
        self.display=display.set_mode((WIDTH,HEIGHT))
        self.title=display.set_caption("贪吃蛇大战")

def main():
    gamewindow=GameWindow(800,600)
    return


if __name__ == '__main__':
    main()
