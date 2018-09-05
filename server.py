#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
test module
"""

__author__ = 'Lin Xin'

from gevent import monkey
monkey.patch_all()
import gevent
import json
from socket import socket
from time import sleep
from threading import Thread
from multiprocessing import Process
from single_snake import Snake


class Server(socket):
    snakes_list = {}

    def __init__(self, host=('0.0.0.0', 12306)):
        super().__init__()
        self.bind(host)
        self.listen(100)
        self.forever_serve()
        print("waiting for connect")

    def forever_serve(self):
        client = Process(target=self._handle_link)
        client.daemon = True
        client.start()
        while True:
            sleep(0.3)
            for snake in Server.snakes_list.values():
                snake.move()
            for client in self.snakes_list:
                client.send(json.dumps(self.snakes_list.values()).encode())

    def _handle_link(self):
        while True:
            client, addr = self.accept()
            print('connect from {}'.format(client.getpeername()))
            t = Thread(target=Server.client_handle, args=(client,))
            t.setDaemon(True)
            t.start()

    def client_handle(self, client):
        print(client.recv(100).decode())
        client_snake = Snake()
        Server.snakes_list[client] = client_snake
        while True:
            command = client.recv(3).decode()
            self.snakes_list[client].control(command)


def main():
    server = Server()
    server.forever_serve()


if __name__ == '__main__':
    main()
