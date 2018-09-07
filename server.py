#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Multi_Snake Server
"""

__author__ = 'Lin Xin'
from gevent import monkey

monkey.patch_all()
import os
import copy
import struct
import pickle
import gevent
from time import sleep
from functools import reduce
from socket import socket
from threading import Thread
from single_snake import Snake, Food, KILL_SELF, FRAME_RATE, SPEED_VAR


class Server(socket):
    snakes_list = {}
    FOOD = None
    r = None

    def __init__(self, host=('0.0.0.0', 12306)):
        super().__init__()
        self.bind(host)
        self.listen(100)
        try:
            self.forever_serve()
        except KeyboardInterrupt:
            print('服务器即将关闭')
            for c in self.snakes_list:
                c.close()
            for i in (3, 2, 1):
                print(i, end='\r')
                sleep(0.5)
            os._exit(0)

    def forever_serve(self):
        client = Thread(target=self._handle_link)
        client.daemon = True
        client.start()
        food = Food()
        Server.FOOD = food
        rate = 1.2 / FRAME_RATE
        running = []
        last_snake_id = 0
        while True:
            sleep(1)
            if not self.snakes_list:
                continue
            else:
                while True:
                    sleep(rate)
                    self.__send_to_client(food)
                    try:
                        max_id = max([snake.id for snake in self.snakes_list.values()])
                    except ValueError:
                        pass
                    if last_snake_id < max_id:
                        break
            while True:
                sleep(rate)
                food = self.__rand_food(food)
                try:
                    max_id = max([snake.id for snake in self.snakes_list.values()])
                except ValueError:
                    pass
                if last_snake_id < max_id:
                    running += [gevent.spawn(self.move, snake, rate) for snake in
                                self.snakes_list.values() if snake.id > last_snake_id]
                    Server.r = running
                    last_snake_id = max_id
                self.__send_to_client(food)
                if all([g.dead for g in running]):
                    print('There is no snake now')
                    break

    def move(self, snake, rate):
        snake_client = self.__find_socket_from_snake(snake)
        while True:
            if snake.is_die:
                break
            sleep(rate * 10 / (SPEED_VAR * (snake.speed - 10) + 10))
            snake.move()
            self.__eat(snake, Server.FOOD)
            self.__killed(snake, snake_client)

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
        sleep(1.6)
        self.snakes_list[client] = client_snake
        client_name = client.getpeername()
        while True:
            try:
                command = client.recv(3).decode()
            except Exception as e:
                print('{} die -----> Reason:{}'.format(client_name, e))
                try:
                    self.snakes_list[client].die()
                    client.close()
                    self.snakes_list.pop(client)
                except:
                    pass
                break
            if command:
                self.snakes_list[client].control(int(command))
            else:
                print('{} close window'.format(client.getpeername()))
                try:
                    self.snakes_list[client].die()
                    client.close()
                    self.snakes_list.pop(client)
                except:
                    pass
                break

    def __snake_body_all(self, food=None):
        snake_body_all = list(reduce(lambda x, y: x + y, [snake.body for snake in self.snakes_list.values()], []))
        if food:
            snake_body_all.append(food.pos)
        return snake_body_all

    def __rand_food(self, food):
        if food.color == (0, 0, 0):
            while True:
                snake_body_all = self.__snake_body_all()
                food = Food(snake_body_all)
                if not food.pos:
                    continue
                break
            Server.FOOD = food
        return food

    @staticmethod
    def __eat(snake, food):
        try:
            if food.pos == snake.body[-1]:
                food.color = (0, 0, 0)
                snake.eat()
        except IndexError:
            return

    def __killed(self, snake, client):
        try:
            for s in self.snakes_list.values():
                if not KILL_SELF and s.id == snake.id:
                    continue
                try:
                    if snake.body[-1] in s.body[:-1]:
                        print('{} die'.format(client.getpeername()))
                        snake.die()
                        break
                    elif snake.body[-1] == s.body[-1]:
                        print('{} and {} kill each other'.format(client.getpeername(),
                                                                 self.__find_socket_from_snake(s).getpeername()))
                        snake.die()
                        s.die()
                        break
                except IndexError:
                    continue
        except RuntimeError:
            self.__killed(snake, client)

    def __send_to_client(self, food):
        snakes_info = pickle.dumps([snake for snake in self.snakes_list.values() if not snake.is_die])
        info_len = struct.pack('6i', len(snakes_info), food.color[0], food.color[1], food.color[2], food.pos[0],
                               food.pos[1])
        try:
            for client in self.snakes_list.keys():
                try:
                    client.send(info_len)
                    client.sendall(snakes_info)
                except (BrokenPipeError, ConnectionResetError, OSError):
                    try:
                        self.snakes_list[client].die()
                        print('{} disconnected'.format(self.snakes_list.pop(client)))
                    except KeyError:
                        pass
                    continue
        except RuntimeError:
            self.__send_to_client(food)

    def __find_socket_from_snake(self, snake):
        return [client for client, s in self.snakes_list.items() if snake == s][0]


def main():
    server = Server()
    server.forever_serve()


if __name__ == '__main__':
    main()
