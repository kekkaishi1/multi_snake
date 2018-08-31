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
from socket import socket
from time import sleep
from threading import Thread
from multiprocessing import Process, Pipe
from single_snake import window_init, draw_line, MyThread, event_handle, Snake


class Server(socket):
    snakes_list = {}

    def __init__(self, host=('0.0.0.0', 12306)):
        super().__init__()
        self.bind(host)
        self.listen(100)
        self.forever_serve()

    @classmethod
    def _init_game(cls, fd1):
        cls.snakes_list = {}
        cls.game_panel = window_init()
        fd1.send(cls.game_panel)
        while True:
            cls.game_panel.fill((0, 0, 0))
            draw_line(cls.game_panel)
            for event in pygame.event.get(KEYDOWN):
                if event.type == pygame.QUIT:
                    sys.exit(0)
            pygame.display.update()

    def forever_serve(self):
        fd1, fd2 = Pipe()
        game = Process(target=self._init_game, args=(fd1,))
        game.start()
        while True:
            print("waiting for connect")
            client, addr = self.accept()
            print('connect from {}'.format(client.getpeername()))
            t = Thread(target=Server.client_handle, args=(client, fd2))
            t.setDaemon(True)
            t.start()

    @classmethod
    def client_handle(cls, client, fd2):
        print(client.recv(100).decode())
        client_snake = Snake()
        client_snake.display(fd2.recv())
        Server.snakes_list[client.getsockname()] = client_snake
        client.send(json.dumps((3, 2, 1)).encode())
        while True:
            command = json.loads(client.recv(100).decode())
            cls.snakes_list[client].move(command.key)
            pygame.display.update()


def main():
    server = Server()
    server.forever_serve()



if __name__ == '__main__':
    main()
