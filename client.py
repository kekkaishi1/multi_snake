#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
test module
"""

__author__ = 'Lin Xin'

import sys
import json
import pygame
from pygame.locals import *
from time import sleep
from socket import socket
import single_snake


class Client(socket):
    def __init__(self, server_host=('127.0.0.1', 12306)):
        super().__init__()
        self.connect(server_host)

    def game_start(self):
        self.send('{} request for game'.format(self.getpeername()).encode())
        for i in json.loads(self.recv(100).decode()):
            print(i, end='\r')
            sleep(0.5)
        print('GO!')
        for event in pygame.event.get(KEYDOWN):
            self.send(json.dumps(event).encode())



def main():
    client = Client()
    command = input("play a game?[y]/n")
    if command == 'n':
        while True:
            command = input("OK, you can play game anywhen you want it with press ENTER")
            if command == '':
                break
    client.game_start()


if __name__ == '__main__':
    main()
