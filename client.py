#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
test module
"""

__author__ = 'Lin Xin'

import sys
import pickle
import pygame
from pygame.locals import *
from time import sleep
from socket import socket
from single_snake import window_init, draw_line,Snake,display_food


class Client(socket):
    def __init__(self, server_host=('127.0.0.1', 12306)):
        super().__init__()
        self.connect(server_host)

    def game_start(self):
        self.send('{} request for game'.format(self.getpeername()).encode())
        for i in (3, 2, 1):
            print(i, end='\r')
            sleep(0.5)
        print('GO!')
        self._init_game()

    def _init_game(self):
        self.game_panel = window_init()
        clock = pygame.time.Clock()
        clock.tick()
        while True:
            clock.tick(30)
            self.game_panel.fill((0, 0, 0))
            draw_line(self.game_panel)
            self._control_snake()
            try:
                info = pickle.unpack('6i',self.recv(24))
            except:
                self.close()
                print('与服务器断开链接')
                sys.exit(0)
            info_len = info[0]
            data = b''
            try:
                for i in range(info_len//1024):
                    data += self.recv(1024)
                if info_len%1024:
                    data += self.recv(info_len%1024)
            except:
                self.close()
                print('与服务器断开链接')
                sys.exit(0)
            snake_list = pickle.loads(data)
            for snake in snake_list:
                snake.display(self.game_panel)
            display_food(self.game_panel,(info[1],info[2],info[3]),info[4],info[5])
            pygame.display.update()

    def _control_snake(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                sys.exit(0)
            if event.type == KEYDOWN and event.key in [273,274,275,276]:
                self.send(str(event.key).encode())


def main():
    client = Client()
    command = input("play a game?[y]/n")
    if command == 'n':
        while True:
            command = input("OK, you can play game whenever you want it with press ENTER")
            if command == '':
                break
    client.game_start()


if __name__ == '__main__':
    main()
