# MIT License
#
# Copyright (c) 2023 [UTN FRA](https://fra.utn.edu.ar/) All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from abc import ABCMeta, abstractmethod
import pygame as pg

class Character(metaclass=ABCMeta):
    """Abstract class of Characters (Player and AI)"""
    def __init__(self, x, y, frame_rate: int = 100, speed_walk: int = 6, speed_run: int = 12, gravity: int = 16, jump: int = 32):
        self.walk_r = list[pg.surface.Surface]()
        self.walk_l = list[pg.surface.Surface]()
        self.stay_r = list[pg.surface.Surface]()
        self.stay_l = list[pg.surface.Surface]()
        self.run_r = list[pg.surface.Surface]()
        self.run_l = list[pg.surface.Surface]()
        self.jump_r = list[pg.surface.Surface]()
        self.jump_l = list[pg.surface.Surface]()
        self.frame = 0
        self.frame_rate = frame_rate
        self.lives = 7
        self.score = 0
        self.animation = self.stay_r
        self.image = self.animation
        #self.rect = self.image.get_rect()
        self.move_x = x
        self.move_y = y
        self.action = 'stay'
        self.speed_walk = speed_walk
        self.speed_run = speed_run
        self.gravity = gravity
        self.jumping = jump
        self.is_jump = False
        self.looking_to_right = True
        self.is_flying = False
        

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self, screen: pg.surface.Surface):
        pass
