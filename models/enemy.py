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
from models.constants import ANCHO_VENTANA, ALTO_VENTANA, debug
from models.hit_points.class_vida import BarraVida
import random as rd


class Enemy(pg.sprite.Sprite):

    def __init__(self, coord_x, coord_y, config_dictionary: dict, frame_rate = 120, speed_walk = 3, speed_run = 6, gravity = 0.85, jump = 32):
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

        # Calibración de parámetros físicos a 60 FPS
        self.__gravity = gravity if gravity <= 2.0 else 0.85
        self.__terminal_velocity = 14.0
        self.__vel_y = 0.0
        self.__pos_y = float(coord_y)
        self.__is_grounded = False

        self.__jump = jump
        self.__is_jumping = False
        self.__initial_frame = 0
        self.__actual_animation = self.__walk_l
        self.__actual_img_animation = self.__actual_animation[self.__initial_frame]
        self.rect = self.__actual_img_animation.get_rect()
        self.rect.x = coord_x
        self.rect.y = coord_y
        self.__pos_y = float(coord_y)
        self.__is_looking_right = False
        self.__max_x_constraint = ANCHO_VENTANA
        self.__max_y_constraint = ALTO_VENTANA
        min_hp = self.__configs.get('enemy_min_hp', 500)
        max_hp = self.__configs.get('enemy_max_hp', min_hp)
        self.__max_hp = rd.randint(min_hp, max_hp)
        self.__hp = self.__max_hp
        bar_width = 50
        bar_height = 5
        self.__life_bar = BarraVida(None, self.__max_hp, self.__hp, bar_width, bar_height, self.rect.centerx - (bar_width // 2), self.rect.top - 10, 'hp')
    
    @property
    def hp_left(self):
        return self.__hp

    @hp_left.setter
    def hp_left(self, hp):
        self.__hp = hp
        if hasattr(self, '_Enemy__life_bar') and self.__life_bar is not None:
            self.__life_bar.actual_amount = self.__hp

    @property
    def max_hp(self) -> int:
        return self.__max_hp

    @property
    def life_bar(self):
        return self.__life_bar

    def take_damage(self, damage: int) -> bool:
        self.__hp = max(0, self.__hp - damage)
        if hasattr(self, '_Enemy__life_bar') and self.__life_bar is not None:
            self.__life_bar.actual_amount = self.__hp
        return self.hp_left <= 0
    
    @property
    def enemy_score(self) -> int:
        return self.__score

    @property
    def is_grounded(self) -> bool:
        return self.__is_grounded

    def cambiar_animacion(self, nueva_animacion: list[pg.surface.Surface]):
        self.__actual_animation = nueva_animacion
        if self.__initial_frame >= len(self.__actual_animation):
            self.__initial_frame = 0
        self.__actual_img_animation = self.__actual_animation[self.__initial_frame]
    
    def stay(self):
        if self.__actual_animation != self.__iddle_l and self.__actual_animation != self.__iddle_r:
            self.cambiar_animacion(self.__iddle_r) if self.__is_looking_right else self.cambiar_animacion(self.__iddle_l)
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
    
    def constraint(self, step_x: int = None):  # Ajusta al enemigo a los límites de la pantalla y alterna patrullaje
        if step_x is None:
            step_x = self.__speed_walk
        if self.__is_looking_right:
            if (self.rect.right + step_x) < self.__max_x_constraint:
                self.rect.x += step_x
            else:
                self.__is_looking_right = False
                self.cambiar_animacion(self.__iddle_l)
                self.stay()
                self.cambiar_animacion(self.__run_l)
                self.run(direction='Left')
        else:
            if self.rect.left - step_x > 0:
                self.rect.x -= step_x
            else:
                self.__is_looking_right = True
                self.cambiar_animacion(self.__iddle_r)
                self.stay()
                self.cambiar_animacion(self.__run_r)
                self.run(direction='Right')
    
    def do_movement(self, delta_ms, floor_y_coord, platforms=None):
        dt_factor = min(delta_ms / 16.667, 2.0) if delta_ms > 0 else 1.0
        step_x = max(1, int(round(self.__speed_walk * dt_factor)))

        # 1. Movimiento horizontal
        self.constraint(step_x)

        # 2. Aceleración por gravedad en velocidad vertical
        self.__vel_y += self.__gravity * dt_factor
        if self.__vel_y > self.__terminal_velocity:
            self.__vel_y = self.__terminal_velocity

        # 3. Integración vertical continua
        prev_bottom = self.rect.bottom
        self.__pos_y += self.__vel_y * dt_factor
        self.rect.y = round(self.__pos_y)

        # 4. Colisión de pies (rect.bottom) con plataformas semi-sólidas al descender
        landed = False
        tolerance = max(16.0, abs(self.__vel_y) * dt_factor + 4.0)

        if platforms and self.__vel_y >= 0:
            for plat in platforms:
                if self.rect.right > plat.rect.left and self.rect.left < plat.rect.right:
                    if prev_bottom <= plat.rect.top + tolerance and self.rect.bottom >= plat.rect.top:
                        self.rect.bottom = plat.rect.top
                        self.__pos_y = float(self.rect.y)
                        self.__vel_y = 0.0
                        self.__is_grounded = True
                        landed = True
                        break

        # 5. Colisión de pies (rect.bottom) con el nivel del suelo base
        if not landed and floor_y_coord and floor_y_coord > 50:
            if self.rect.bottom >= floor_y_coord:
                self.rect.bottom = floor_y_coord
                self.__pos_y = float(self.rect.y)
                self.__vel_y = 0.0
                self.__is_grounded = True
                landed = True

        if not landed:
            self.__is_grounded = False
    
    def do_animation(self, delta_ms):
        self.__player_animation_time += delta_ms
        if self.__player_animation_time >= self.__frame_rate:
            self.__player_animation_time = 0
            if self.__initial_frame < len(self.__actual_animation) - 1:
                self.__initial_frame += 1
            else:
                self.__initial_frame = 0
            self.__actual_img_animation = self.__actual_animation[self.__initial_frame]

    def draw(self, screen: pg.surface.Surface):
        if screen is None:
            return
        if debug.get('actual_status'):
            pg.draw.rect(screen, (0, 0, 255), self.rect, 2)
        screen.blit(self.__actual_img_animation, self.rect)
        if hasattr(self, '_Enemy__life_bar') and self.__life_bar is not None:
            bar_x = self.rect.centerx - (self.__life_bar.ancho // 2)
            bar_y = max(2, self.rect.top - 10)
            pg.draw.rect(screen, (0, 0, 0), (bar_x - 1, bar_y - 1, self.__life_bar.ancho + 2, self.__life_bar.alto + 2), 1)
            self.__life_bar.update(screen, bar_x, bar_y, self.__hp)
    
    def update(self, delta_ms, screen: pg.surface.Surface, floor_y_coord: int, platforms=None):
        self.do_movement(delta_ms, floor_y_coord, platforms)
        self.do_animation(delta_ms)
        self.draw(screen)
