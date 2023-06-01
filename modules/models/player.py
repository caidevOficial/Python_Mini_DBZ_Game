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

import pygame as pg
from modules.models.character import Character
from modules.auxiliar.common_variables import (
    PLAYER_WALK_SPRITE, PLAYER_IDLE_SPRITE, PLAYER_JUMP_SPRITE, 
    PLAYER_ATTACK_SPRITE, PLAYER_RUN_SPRITE, WINDOWS_WIDTH
)
from modules.auxiliar.auxiliar import Auxiliar


class Player(Character):

    def __init__(self, x, y, frame_rate: int = 100, speed_walk: int = 6, speed_run: int = 12, gravity: int = 16, jump: int = 32):
        """
        It takes the spritesheet and creates a list of images from it.
        """
        super().__init__(x, y, frame_rate, speed_walk, speed_run, gravity, jump)
        self.walk_r = Auxiliar.get_surface_from_spritesheet(PLAYER_WALK_SPRITE, 6, 1)
        self.walk_l = Auxiliar.get_surface_from_spritesheet(PLAYER_WALK_SPRITE, 6, 1, flip=True)
        self.run_r = Auxiliar.get_surface_from_spritesheet(PLAYER_RUN_SPRITE, 6, 1)
        self.run_l = Auxiliar.get_surface_from_spritesheet(PLAYER_RUN_SPRITE, 6, 1, flip=True)
        self.stay_r = Auxiliar.get_surface_from_spritesheet(PLAYER_IDLE_SPRITE, 6, 1)
        self.stay_l = Auxiliar.get_surface_from_spritesheet(PLAYER_IDLE_SPRITE, 6, 1, flip=True)
        self.jump_r = Auxiliar.get_surface_from_spritesheet(PLAYER_JUMP_SPRITE, 6, 1)
        self.jump_l = Auxiliar.get_surface_from_spritesheet(PLAYER_JUMP_SPRITE, 6, 1, flip=True)
        self.attack_r = Auxiliar.get_surface_from_spritesheet(PLAYER_ATTACK_SPRITE, 6, 1)
        self.attack_l = Auxiliar.get_surface_from_spritesheet(PLAYER_ATTACK_SPRITE, 6, 1, flip=True)
        self.frame = 0
        self.animation = self.stay_r
        self.image = self.animation[self.frame]
        self.rect = self.image.get_rect()
        self.player_time_move = 0
        self.player_time_animation = 0
        self.max_jumping_h = self.image.get_rect().bottom - self.image.get_rect().top
        # self.lives = 7
        # self.score = 0
        # self.move_x = x
        # self.move_y = y
        # self.action = 'stay'
        # self.speed_walk = speed_walk
        # self.speed_run = speed_run
        # self.gravity = gravity
        # self.jump = jump
        # self.is_jump = False
        # self.looking_to_right = True

    def __set_direction_animation(self, player_sprites: list[pg.surface.Surface]):
        pass

    def __set_x_animations_preset(self, move_x, animation: list[pg.surface.Surface], look_r: bool = True, is_jump: bool = True):
        self.move_x = move_x
        self.animation = animation
        self.looking_to_right = look_r
        self.is_jump = is_jump
        # self.frame = frame
    
    def __set_y_animations_preset(self):
        self.move_y = -self.jumping
        self.move_x = self.speed_run if self.looking_to_right else -self.speed_run
        self.animation = self.jump_r if self.looking_to_right else self.jump_l
        self.frame = 0
        self.is_jump = True

    def __check_direction(self, new_direction: bool):
        return self.looking_to_right == new_direction
    
    def __reset_frame(self, animation_l: list[pg.surface.Surface], animation_r: list[pg.surface.Surface]):
        changes = self.animation != animation_l or self.animation != animation_r
        if changes:
            self.frame = 0

    def walk(self, direction: str):
        look_right = False
        match direction:
            case 'Right':
                look_right = True
                self.__set_x_animations_preset(self.speed_walk, self.walk_r, look_r=look_right, is_jump=False)
            case 'Left':
                look_right = False
                self.__set_x_animations_preset(-self.speed_walk, self.walk_l, look_r=look_right, is_jump=False)
        if self.__check_direction(look_right):
            self.__reset_frame(self.walk_l, self.walk_r)

    def run(self, direction: str):
        look_right = False
        match direction:
            case 'Right':
                look_right = True
                self.__set_x_animations_preset(self.speed_run, self.run_r, look_r=look_right, is_jump=False)
            case 'Left':
                look_right = False
                self.__set_x_animations_preset(-self.speed_run, self.run_l, look_r=look_right, is_jump=False)
        if self.__check_direction(look_right):
            self.__reset_frame(self.run_l, self.run_r)
    
    def stay(self):
        if self.animation != self.stay_l and self.animation != self.stay_r:
            self.animation = self.stay_r if self.looking_to_right else self.stay_l
            self.frame = 0
            self.move_x = 0
            self.move_y = 0
        
    def check_jump_height(self):
        if self.image.get_rect().top > self.max_jumping_h:
            return True

    def jump(self, jumping=True):
        if jumping and not self.is_jump:
            self.__set_y_animations_preset()
        else:
            self.is_jump = False
            self.stay()

    def die(self):
        pass
    
    def attack(self):
        self.animation = self.attack_r if self.looking_to_right else self.attack_l

    def fly_up(self):
        self.is_flying = True

    def fly_down(self):
        self.is_flying = False

    def __set_border_limits(self, direction: int) -> int:
        pixels_move = 0
        if self.move_x > 0:
            pixels_move = self.move_x if self.rect.x < WINDOWS_WIDTH - 67 else 0
        elif self.move_x < 0:
            pixels_move = self.move_x if self.rect.x > 0 else 0
        return pixels_move

    def do_movement(self, delta_ms: int) -> None:
        """
        If the player_time_move is greater than or equal to the frame_rate, then the player_time_move is set
        to 0, the player's x and y coordinates are set to the __set_border_limits function, and if the
        player's y coordinate is less than 410, then the player's y coordinate is set to the gravity.
        
        :param delta_ms: The time in milliseconds since the last frame
        :type delta_ms: int
        """
        self.player_time_move += delta_ms
        if self.player_time_move >= self.frame_rate:
            self.player_time_move = 0
            self.rect.x += self.__set_border_limits(self.move_x)
            self.rect.y += self.move_y
            if self.rect.y < 410:
                self.rect.y += self.gravity

    def do_animation(self, delta_ms: int) -> None:
        """
        If the time since the last frame change is greater than the frame rate, change the frame
        
        :param delta_ms: The time in milliseconds since the last frame
        :type delta_ms: int
        """
        self.player_time_animation += delta_ms
        if self.player_time_animation >= self.frame_rate:
            self.player_time_animation = 0
            if self.frame < len(self.animation)-1:
                self.frame += 1
            else:
                self.frame = 0
                if self.is_jump:
                    self.is_jump = False
                    self.move_y = 0

    def update(self, delta_ms: int) -> None:
        """
        The function updates the animation and movement of the sprite
        
        :param delta_ms: The time in milliseconds since the last update
        :type delta_ms: int
        """
        self.do_movement(delta_ms)
        self.do_animation(delta_ms)


    def draw(self, screen: pg.surface.Surface) -> None:
        """
        It draws the image of the animation to the screen.
        
        :param screen: pg.Surface
        """
        self.image = self.animation[self.frame]
        # self.rect = self.image.get_rect()
        screen.blit(self.image, self.rect)
