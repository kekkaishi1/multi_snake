#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
test module
"""

__author__ = 'Lin Xin'

from gevent import monkey

monkey.patch_all()
import gevent
import os
import copy
import struct
import pickle
from socket import socket
from time import sleep
from threading import Thread
from functools import reduce
from common.config import get_config
from single_snake import Snake, Food

config = get_config()
GAME_PANEL_SIZE = config['GAME_PANEL_SIZE']  # 游戏面板行列数
GAME_PANEL_SIZE_X = GAME_PANEL_SIZE['X']  # 游戏面板列数
GAME_PANEL_SIZE_Y = GAME_PANEL_SIZE['Y']  # 游戏面板行数
KILL_SELF = config['KILL_SELF']  # 允许自残


class Server(socket):
    snakes_list = {}
    FOOD = None

    def __init__(self, host=('0.0.0.0', 12306)):
        super().__init__()
        self.bind(host)
        self.listen(100)
        self.forever_serve()

    def forever_serve(self):
        client = Thread(target=self._handle_link)
        client.daemon = True
        client.start()
        food = Food()
        try:
            while True:
                sleep(0.08)
                if not self.snakes_list:
                    continue

                if food.color == (0, 0, 0):
                    while True:
                        snake_body_all = self.__snake_body_all()
                        food = Food(snake_body_all)
                        if not food.pos:
                            continue
                        break
                    Server.FOOD = food
                snakes_head = {client: snake.move() for client, snake in self.snakes_list.items()}
                for client, head in snakes_head.items():
                    if head == food.pos:
                        food.color = (0, 0, 0)
                        self.snakes_list[client].eat()
                        break
                snakes_origin = copy.deepcopy([snake for snake in self.snakes_list.values()])
                for client, head in snakes_head.items():
                    for snake in snakes_origin:
                        if not KILL_SELF and self.snakes_list[client].id == snake.id:
                            continue
                        if head in snake.body[0:-1]:
                            try:
                                print('{} die'.format(client.getpeername()))
                                self.snakes_list[client].die()
                                break
                            except KeyError:
                                break
                snakes_info = pickle.dumps(list(self.snakes_list.values()))
                info_len = struct.pack('6i', len(snakes_info), food.color[0], food.color[1], food.color[2], food.pos[0],
                                       food.pos[1])
                for client in self.snakes_list:
                    try:
                        client.send(info_len)
                        client.sendall(snakes_info)
                    except BrokenPipeError or ConnectionResetError:
                        self.snakes_list.pop(client)
                        continue
        except KeyboardInterrupt:
            print('服务器即将关闭')
            for c in self.snakes_list:
                c.close()
            for i in (3, 2, 1):
                print(i, end='\r')
                sleep(0.5)
            os._exit(0)

    def _handle_link(self):
        while True:
            print('waiting for connect')
            client, addr = self.accept()
            print('connect from {}'.format(client.getpeername()))
            gevent.spawn(self._client_handle, client)

    def _client_handle(self, client):
        print(client.recv(100).decode())
        while True:
            snake_body_all = self.__snake_body_all(Server.FOOD)
            client_snake = Snake(snake_body_all)
            if client_snake.body:
                break
        sleep(1)
        self.snakes_list[client] = client_snake
        client_name = client.getpeername()
        while True:
            try:
                command = client.recv(3).decode()
            except:
                print('{} die'.format(client_name))
                client.close()
                self.snakes_list.pop(client)
                break
            if command:
                self.snakes_list[client].control(int(command))
            else:
                print('{} die'.format(client.getpeername()))
                client.close()
                self.snakes_list.pop(client)
                break

    def __snake_body_all(self, food=None):
        snake_body_all = list(reduce(lambda x, y: x + y, [snake.body for snake in self.snakes_list.values()], []))
        if food:
            snake_body_all.append(food.pos)
        return snake_body_all


def main():
    server = Server()
    server.forever_serve()


if __name__ == '__main__':
    main()
