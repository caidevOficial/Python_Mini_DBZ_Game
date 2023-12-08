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

from models.surface_manager import SurfaceManager as sf
import pygame as pg
from models.constantes import ANCHO_VENTANA, ALTO_VENTANA
from models.hit_points.class_vida import BarraVida
import random as rd


class Enemy(pg.sprite.Sprite):

    def __init__(self, coord_x, coord_y, config_dictionary: dict, frame_rate = 120, speed_walk = 3, speed_run = 6, gravity = 16, jump = 32):
        super().__init__()
        self.__configs = config_dictionary
        self.__iddle_r = sf.get_surface_from_spritesheet(self.__configs.get('sprites').get('iddle').get('path'), self.__configs.get('sprites').get('iddle').get('amount_images'), 1)
        self.__iddle_l = sf.get_surface_from_spritesheet(self.__configs.get('sprites').get('iddle').get('path'), self.__configs.get('sprites').get('iddle').get('amount_images'), 1, flip=True)
        self.__walk_r = sf.get_surface_from_spritesheet(self.__configs.get('sprites').get('walk').get('path'), self.__configs.get('sprites').get('walk').get('amount_images'), 1)
        self.__walk_l = sf.get_surface_from_spritesheet(self.__configs.get('sprites').get('walk').get('path'), self.__configs.get('sprites').get('walk').get('amount_images'), 1, flip=True)
        self.__run_r = sf.get_surface_from_spritesheet(self.__configs.get('sprites').get('run').get('path'), self.__configs.get('sprites').get('run').get('amount_images'), 1)
        self.__run_l = sf.get_surface_from_spritesheet(self.__configs.get('sprites').get('run').get('path'), self.__configs.get('sprites').get('run').get('amount_images'), 1, flip=True)
        self.__attack_r = sf.get_surface_from_spritesheet(self.__configs.get('sprites').get('attack').get('path'), self.__configs.get('sprites').get('attack').get('amount_images'), 1)
        self.__attack_l = sf.get_surface_from_spritesheet(self.__configs.get('sprites').get('attack').get('path'), self.__configs.get('sprites').get('attack').get('amount_images'), 1, flip=True)
        self.__bullet_group = pg.sprite.Group()
        self.__move_x = 0
        self.__move_y = 0
        self.__score = int(self.__configs.get('enemies_score'))
        self.__speed_walk = speed_walk
        self.__speed_run = speed_run
        self.__frame_rate = frame_rate
        self.__time_move = 0
        self.__player_animation_time = 0
        self.__gravity = gravity
        self.__jump = jump
        self.__is_jumping = False
        self.__initial_frame = 0
        self.__actual_animation = self.__walk_l
        self.__actual_img_animation = self.__actual_animation[self.__initial_frame]
        self.rect = self.__actual_img_animation.get_rect()
        self.rect.x = coord_x
        self.rect.y = coord_y
        self.__is_looking_right = False
        self.__max_x_constraint = ANCHO_VENTANA
        self.__max_y_constraint = ALTO_VENTANA
        self.__hp = rd.randint(self.__configs.get('enemy_min_hp'), self.__configs.get('enemy_max_hp'))
    
    @property
    def hp_left(self):
        return self.__hp

    @hp_left.setter
    def hp_left(self, hp):
        self.__hp += hp
    
    @property
    def enemy_score(self) -> int:
        return self.__score

    def cambiar_animacion(self, nueva_animacion: list[pg.surface.Surface]):
        self.__actual_animation = nueva_animacion
        if self.__initial_frame > 0:
            self.__initial_frame = 0
        self.__actual_img_animation = self.__actual_animation[self.__initial_frame]
    
    def stay(self):
        if self.__actual_animation != self.__iddle_l and self.__actual_animation != self.__iddle_r:
            self.cambiar_animacion(self.__iddle_r) if self.__is_looking_right else  self.cambiar_animacion(self.__iddle_l)
            self.__move_x = 0
            self.__move_y = 0
    
    def __set_x_animations_preset(self, move_x, animation_list: list[pg.surface.Surface], look_r: bool):
        self.__move_x = move_x
        self.__actual_animation = animation_list
        self.__is_looking_right = look_r
    
    def run(self, direction: str = 'Right'):
        self.__initial_frame = 0
        match direction:
            case 'Right':
                look_right = True
                self.__set_x_animations_preset(self.__speed_run, self.__run_r, look_r=look_right)
            case 'Left':
                look_right = False
                self.__set_x_animations_preset(-self.__speed_run, self.__run_l, look_r=look_right)
    
    def constraint(self):  # Ajusta al jugador a los limites de la pantalla
        if self.__is_looking_right:
            if (self.rect.right + self.__speed_walk ) < self.__max_x_constraint:
                #self.__rect.left += self.__speed_walk
                self.rect.x += self.__speed_walk
            else:
                self.__is_looking_right = False
                self.cambiar_animacion(self.__iddle_l)
                self.stay()
                self.cambiar_animacion(self.__run_l)
                self.run(direction='Left')
        else:
            if self.rect.left - self.__speed_walk > 0:
                #self.__rect.right -= self.__speed_walk
                self.rect.x -= self.__speed_walk
            else:
                self.__is_looking_right = True
                self.cambiar_animacion(self.__iddle_r)
                self.stay()
                self.cambiar_animacion(self.__run_r)
                self.run(direction='Right')
    
    def do_movement(self, delta_ms, floor_y_coord):
        self.__time_move += delta_ms
        if self.__time_move >= self.__frame_rate:
            self.constraint()
            if self.rect.y < floor_y_coord:
                self.rect.y += self.__gravity
            else: self.rect.y += self.__move_y
    
    def do_animation(self, delta_ms):
        self.__player_animation_time += delta_ms
        if self.__player_animation_time >= self.__frame_rate:
            self.__player_animation_time = 0
            if self.__initial_frame < len(self.__actual_animation) - 1:
                self.__initial_frame += 1
            else:
                self.__initial_frame = 0

    def draw(self, screen: pg.surface.Surface):
        screen.blit(self.__actual_img_animation, self.rect)
    
    def update(self, delta_ms, screen: pg.surface.Surface, floor_y_coord: int):
        self.do_movement(delta_ms, floor_y_coord)
        self.draw(screen)
        #self.constraint()