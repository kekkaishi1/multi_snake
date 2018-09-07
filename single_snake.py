#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Multi_Snake Config
"""

__author__ = 'Lin Xin'

import os
import sys
import pygame
from random import randint, choice
from common.config import get_config, get_resource, get_settings

# 配置文件
config = get_config()
BLOCK_SIZE = config['BLOCK_SIZE']  # 蛇单块大小
GAME_PANEL_SIZE = config['GAME_PANEL_SIZE']  # 游戏面板行列数
GAME_PANEL_SIZE_X = GAME_PANEL_SIZE['X']  # 游戏面板列数
GAME_PANEL_SIZE_Y = GAME_PANEL_SIZE['Y']  # 游戏面板行数
WINDOW_WIDTH = GAME_PANEL_SIZE_X * (BLOCK_SIZE + 1) - 1  # 游戏面板横向像素值
WINDOW_HEIGHT = GAME_PANEL_SIZE_Y * (BLOCK_SIZE + 1) - 1  # 游戏面板纵向像素值
WINDOW_RESOLUTION = (WINDOW_WIDTH, WINDOW_HEIGHT)  # 游戏面板分辨率
FULL_SCREEN_OR_NOT = config['FULL_SCREEN']  # 是否全屏
LINE_COLOR = config['LINE_COLOR']  # 格子线颜色
KILL_SELF = config['KILL_SELF']  # 允许自残
FRAME_RATE = config['FRAME_RATE']  # 帧率
SPEED_VAR = config["SPEED_VAR"]  # 速度补偿参数 0~+∞ 0无差异

# 游戏配置
settings = get_settings()

# 资源文件
resourses_path = '{}\\resources'.format(sys.path[0])
resourses = get_resource()
BACKGROUND_IMAGE = os.path.join(resourses_path, resourses['BACKGROUND'])


class Snake:
    # 273:UP    274:DOWN    275:RIGHT   276:LEFT
    DIRECTION = {273: lambda x: (x[0], x[1] - 1), 274: lambda x: (x[0], x[1] + 1),
                 276: lambda x: (x[0] - 1, x[1]), 275: lambda x: (x[0] + 1, x[1])}
    MOVE_ONE = [(x, y) for x in (1, -1, 0) for y in (1, -1, 0) if (x, y).count(0) == 1]

    ID = 0

    def __init__(self, snake_body_all):
        rand_body = self._random_init_body()
        if True in [block in snake_body_all for block in rand_body]:
            self.body = False
        else:
            self.body = rand_body  # 范围 0~极限-1
        self.speed = 10
        self.color = self.__rand_color()
        self.direction = self.__get_direction()
        self.is_die = False
        self.eat_status = False
        Snake.ID += 1
        self.id = Snake.ID

    def display(self, screen):
        for block in self.body:
            rect_x_0 = block[0] * (BLOCK_SIZE + 1)
            rect_y_0 = block[1] * (BLOCK_SIZE + 1)
            rect = (rect_x_0, rect_y_0, 11, 11)
            pygame.draw.rect(screen, self.color, rect)

    def move(self):
        if not self.is_die:
            if not self.eat_status:
                self.body = self.body[1:] + [Snake.DIRECTION[self.direction](self.body[-1])]
            else:
                self.body = self.body[:] + [Snake.DIRECTION[self.direction](self.body[-1])]
                self.eat_status = False
            if self.body[-1][0] // GAME_PANEL_SIZE_X:  # 超出屏幕范围
                self.body[-1] = (self.body[-1][0] % GAME_PANEL_SIZE_X, self.body[-1][1])
            if self.body[-1][1] // GAME_PANEL_SIZE_Y:
                self.body[-1] = (self.body[-1][0], self.body[-1][1] % GAME_PANEL_SIZE_Y)
            return self.body[-1]

    def control(self, event):
        try:
            if abs(event - self.__get_direction()) != 1 or event + self.__get_direction() == 549:
                self.direction = event
        except IndexError:
            pass

    def eat(self):
        self.eat_status = True
        self.speed += 1

    def die(self):
        self.is_die = True
        self.body = []
        self.speed = 0

    @staticmethod
    def __rand_color():
        while True:
            colour = tuple([randint(100, 200) for _ in range(3)])
            if colour == (0, 0, 0):
                continue
            return colour

    def __get_direction(self):
        for m, n in zip(self.body[-1], self.body[-2]):
            if m < n:
                return 276
            elif m > n:
                return 275
            else:
                if self.body[-1][1] < self.body[-2][1]:
                    return 273
                else:
                    return 274

    def _random_init_body(self, body=None):
        if not body:
            body = [(randint(0, GAME_PANEL_SIZE_X), randint(0, GAME_PANEL_SIZE_Y))]
        last_block = self.location_add(body[-1], choice(self.MOVE_ONE))
        body.append(last_block)
        if len(body) == 4:
            return body
        return self._random_init_body(body)

    @staticmethod
    def location_add(l1, l2):
        new_location = l1[0] + l2[0], l1[1] + l2[1]
        return new_location


def draw_line(screen):
    block = BLOCK_SIZE + 1
    for x in range(GAME_PANEL_SIZE_Y):
        pygame.draw.line(screen, LINE_COLOR, (0, block * x), (WINDOW_WIDTH, block * x))
    for y in range(GAME_PANEL_SIZE_X):
        pygame.draw.line(screen, LINE_COLOR, (block * y, 0), (block * y, WINDOW_HEIGHT))


def window_init():
    screen = pygame.display.set_mode(WINDOW_RESOLUTION, FULL_SCREEN_OR_NOT)
    pygame.display.set_caption("贪吃蛇大战")
    if settings['background']:
        background = pygame.image.load(BACKGROUND_IMAGE).convert()  # convert_alpha
        screen.blit(background, (0, 0))
    draw_line(screen)
    return screen


def display_food(screen, colour, pos_x, pos_y):
    pygame.draw.rect(screen, colour, (pos_x * (BLOCK_SIZE + 1) + 1, pos_y * (BLOCK_SIZE + 1) + 1, 11, 11))


class Food:
    def __init__(self, snake_body_all=None, colour=(255, 255, 255)):
        self.color = colour
        pos = (randint(3, GAME_PANEL_SIZE_X - 3), randint(3, GAME_PANEL_SIZE_Y - 3))
        if snake_body_all and pos in snake_body_all:
            pos = None
        self.pos = pos
