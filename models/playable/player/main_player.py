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
from models.constantes import ANCHO_VENTANA, DEBUG
from models.hit_points.class_vida import BarraVida
from models.playable.player.metricas import Metrics
from models.blasts.ki_blast import KiBlast
from models.blasts.kamehame import Kamehame
import pygame.mixer as mixer


class Player(pg.sprite.Sprite):

    def __init__(self, screen: pg.surface.Surface, coord_x, coord_y, frame_rate = 100, speed_walk = 6, speed_run = 12, gravity = 16, jump = 32):
        super().__init__()
        mixer.init()
        self.__player_control = False
        self.__is_base_state = True
        self.__is_base_transforming = False
        self.__time_until_initial_transform_c = 3800
        self.__time_until_initial_transform_c2 = 7982
        self.__time_until_control = 12454
        self.__main_screen_surface = screen
        self.__metrics = Metrics()
        self.__set_base_sprites()
        #self.__set_transform_sprites()
        self.__sound_path = './assets/sound/'
        self.__sound_fx = [
            mixer.Sound(f'{self.__sound_path}charge_ssj1.mp3'),
            mixer.Sound(f'{self.__sound_path}ki_blast.mp3'),
            mixer.Sound(f'{self.__sound_path}charge_ssj2.mp3'),
            mixer.Sound(f'{self.__sound_path}kamehameha_charge_f.mp3'),
            mixer.Sound(f'{self.__sound_path}kamehameha_shoot.mp3'),
            mixer.Sound(f'{self.__sound_path}initial_transform.mp3')
        ]
        self.__actual_hp = None
        self.__max_hp_by_level = None
        self.__actual_mp = None
        self.__max_mp_by_level = None
        self.__move_x = 0
        self.__move_y = 0
        self.__speed_walk = speed_walk
        self.__speed_run = speed_run
        self.__frame_rate = frame_rate
        self.__player_move_time = 0
        self.__player_animation_time = 0
        self.__gravity = gravity
        self.__jump_power = jump
        self.__is_jumping = False
        self.__is_falling = False
        self.__initial_frame = 0
        self.__actual_animation = self.__iddle_base_r
        self.__actual_img_animation = self.__actual_animation[self.__initial_frame]
        self.rect = self.__actual_img_animation.get_rect()
        self.rect.x = coord_x
        self.rect.y = coord_y
        self.__is_looking_right = True
        self.__bullet_group = pg.sprite.Group()
        self.__puntaje = 0
        self.__metrics.score_gained = 0
        #self.__ready_to_attack = True
        self.__ki_blast_time = 0
        self.__ki_blast_cooldown = 1500
        self.__ki_blast_energy_cost = 200
        self.__y_start_jump = 0
        self.rect_ground_collision = pg.Rect(self.rect.x+100,self.rect.y+10 + self.rect.h-50,self.rect.w/3,10 )
        self.__gravity_vel_y = 0
        self.__is_charging = False
        self.__is_transformed = False
        self.__is_charging_kame = False
        self.__is_shooting_kame = False
        self.__kame_charge_time = 0
        self.__kame_charge_init_time = 0
        self.__kame_shoot_time = 0
        self.__kame_shoot_init_time = 0
        self.__kame_energy_cost = 1500
        # self.__kame_fully_charged_time = 7408
        self.__kame_fully_charged_time = 10594
    
    @property
    def actual_hit_points(self):
        return self.self.__life_bar.actual_amount
    
    @actual_hit_points.setter
    def actual_hit_points(self, hit_points):
        if hit_points > 0 and self.__actual_hp + hit_points <= self.__max_hp_by_level:
            self.__actual_hp += hit_points
        elif hit_points > 0 and self.__actual_hp + hit_points <= self.__max_hp_by_level:
            self.__actual_hp = self.__max_hp_by_level
        elif hit_points < 0 and self.__actual_hp - hit_points >= 0:
            self.__actual_hp -= hit_points
        else:
            self.__actual_hp = 0
        self.__life_bar.actual_amount = self.__actual_hp
    
    @property
    def max_hit_points(self):
        return self.__life_bar.max_amount
    
    @max_hit_points.setter
    def max_hit_points(self, max_hp):
        self.__max_hp_by_level = max_hp
        self.__life_bar.max_amount = max_hp
    
    @property
    def actual_mana_points(self):
        return self.__mana_bar.actual_amount
    
    @actual_mana_points.setter
    def actual_mana_points(self, mana_points):
        if ((mana_points > 0 and self.__actual_mp + mana_points <= self.__max_mp_by_level) or 
            (mana_points < 0 and self.__actual_mp + mana_points >= 0)):
            self.__actual_mp += mana_points
        elif mana_points > 0 and self.__actual_mp + mana_points >= self.__max_mp_by_level:
            self.__actual_mp = self.__max_mp_by_level
        self.__mana_bar.actual_amount = self.__actual_mp
        if DEBUG:
            print(self.__mana_bar.actual_amount, self.__actual_mp)
    
    @property
    def max_mana_points(self):
        return self.__mana_bar.max_amount
    
    @max_mana_points.setter
    def max_mana_points(self, max_mp):
        self.__max_mp_by_level = max_mp
        self.__mana_bar.max_amount = max_mp
    
    @property
    def mana_bar(self):
        return self.__mana_bar
    
    @property
    def life_bar(self):
        return self.__life_bar
    
    @property
    def puntaje(self) -> int:
        return self.__metrics.score_gained
    
    @puntaje.setter
    def puntaje(self, puntos: int):
        self.__metrics.score_gained += puntos
    
    @property
    def get_blasts(self):
        return self.__bullet_group

    def __check_can_shoot(self, attack_type: str) -> bool:
        attack_cost = 0
        match attack_type:
            case 'ki_blast':
                attack_cost = self.__ki_blast_energy_cost
            case 'super':
                attack_cost = self.__kame_energy_cost
        if DEBUG:
            print(f'Attack cost: {attack_cost}')
            print(f'Actual mana points: {self.__actual_mp}')
        return self.__actual_mp - attack_cost >= 0

    def __sound_player(self, sound_name: pg.mixer.Sound, play_stop: str, volume: float):
        match play_stop:
            case 'play':
                sound_name.set_volume(volume)
                sound_name.play()
            case 'stop':
                sound_name.fadeout(1000)
    
    def __set_x_animations_preset(self, move_x, animation_list: list[pg.surface.Surface], look_r: bool):
        self.__move_x = move_x
        self.__actual_animation = animation_list
        self.__is_looking_right = look_r
    
    def __set_y_animations_preset(self):
        self.__move_y = -self.__jump_power
        self.__move_x = self.__speed_run if self.__is_looking_right else -self.__speed_run
        self.change_animation(self.__jump_r) if self.__is_looking_right else  self.change_animation(self.__jump_l)
        #self.__actual_animation = self.__jump_r if self.__is_looking_right else self.__jump_l
        #self.__initial_frame = 0
        self.__is_jumping = True
    
    def change_x(self,delta_x):
        self.rect.x += delta_x
        self.rect_corrected.x += delta_x
        self.rect_ground_collision.x += delta_x

    def change_y(self,delta_y):
        self.rect.y += delta_y
        self.rect_corrected.y += delta_y
        self.rect_ground_collision.y += delta_y

    def jump(self, on_off: bool):
        #if self.is_alive and self.can_jump:
            #if self.rect_corrected.y + self.__jump_power > 40:
                if(on_off and not self.__is_jumping and not self.__is_falling):
                    self.__y_start_jump = self.rect.y
                    if(self.__is_looking_right):
                        self.__move_x = int(self.__move_x / 2)
                        self.__move_y = -self.__jump_power
                        self.__actual_animation = self.__jump_r
                    else:
                        self.__move_x = int(self.__move_x / 2)
                        self.__move_y = -self.__jump_power
                        self.__actual_animation = self.__jump_l
                    self.__initial_frame = 0
                    self.__is_jumping = True
                if not on_off:
                    self.__is_jumping = False
                    self.stay()

    def add_gravity(self)-> None:
        self.__gravity_vel_y += 1
        if(self.__gravity_vel_y > 10):
            self.__gravity_vel_y = 10
        self.dy = self.__gravity_vel_y

    def __set_borders_limits(self):
        pixels_move = 0
        if self.__move_x > 0:
            pixels_move = self.__move_x if self.rect.x < ANCHO_VENTANA - self.__actual_img_animation.get_width() else 0
        elif self.__move_x < 0:
            pixels_move = self.__move_x if self.rect.x > 0 else 0
        return pixels_move

    def do_movement(self, delta_ms, floor_y_coord):
        self.__player_move_time += delta_ms
        if self.__player_move_time >= self.__frame_rate:
            self.__player_move_time = 0
            self.rect.x += self.__set_borders_limits()
            # Parte relacionado a saltar
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
                # if self.__is_jumping:
                #     self.__is_jumping = False
                #     self.__move_y = 0
    
    def __cooldown_ready_to_action(self) -> bool:
        curent_time = pg.time.get_ticks()
        return curent_time - self.__ki_blast_time >= self.__ki_blast_cooldown
    
    def __cooldown_charge_super(self):
        curent_time = pg.time.get_ticks()
        return curent_time - self.__kame_charge_time >= 10000
    
    def __cooldown_shoot_super(self):
        curent_time = pg.time.get_ticks()
        return curent_time - self.__kame_shoot_time >= 7000

    # def recharge(self):
    #     if not self.__ready_to_attack:
    #         if self.__cooldown_ready_to_action():
    #             self.__ready_to_attack = True
    #! Sounds related
    def mute_sounds(self, sound_type: str) -> None:
        match sound_type:
            case 'charge_kame':
                if self.__is_transformed:
                    self.__sound_fx[3].fadeout(500)
            case 'charge':
                self.__sound_fx[0].fadeout(500)
                self.__sound_fx[2].fadeout(500)

    def initial_config(self, max_hp, max_mp):
        self.__max_hp_by_level = max_hp
        self.__max_mp_by_level = max_mp
        self.__actual_hp = max_hp
        self.__actual_mp = max_mp
        self.__life_bar = BarraVida(self.__main_screen_surface, self.__max_hp_by_level, self.__actual_hp, 100, 5 , self.rect.centerx+50, self.rect.y -80, 'hp')
        self.__mana_bar = BarraVida(self.__main_screen_surface, self.__max_mp_by_level, self.__actual_mp, 100, 5 , self.rect.centerx+50, self.rect.y -20, 'mp')
    
    def initial_level_coords(self, coord_x: int, coord_y: int) -> None:
        self.rect.x = coord_x
        self.rect.y = coord_y
    
    def __initial_transform(self, delta_ms: int):
        current_time = pg.time.get_ticks()
        if not self.__player_control:
            if self.__is_base_state and not self.__is_base_transforming:
                if current_time >= self.__time_until_initial_transform_c and current_time < self.__time_until_initial_transform_c2:
                    self.change_animation(self.__charge_base_r)
                    self.__is_base_transforming = True
                    self.__sound_player(self.__sound_fx[5], 'play', 0.3)
                    if DEBUG: print(f'1° IF: current time: {current_time} | delta: {delta_ms} | transf: {self.__is_base_transforming}')
            elif self.__is_base_state and self.__is_base_transforming:
                if current_time >= self.__time_until_initial_transform_c2:
                    self.change_animation(self.__charge_r)
                    self.__is_base_state = False
                    if DEBUG: print(f'2° IF: current time: {current_time} | delta: {delta_ms} | base: {self.__is_base_state}')
            elif not self.__is_base_state and self.__is_base_transforming:
                if current_time >= self.__time_until_control:
                    self.change_animation(self.__iddle_r)
                    self.__is_base_transforming = False
                    self.__player_control = True
                    if DEBUG: print(f'3° IF: current time: {current_time} | delta: {delta_ms} | control: {self.__player_control}')
        else:
            self.__sound_player(self.__sound_fx[5], 'stop', 0.3)


    #! ACCIONES
    def __create_ki_power(self, type: str = 'ki_blast'):
        if self.__is_looking_right:
            direction = self.rect.right
            direction_str = 'right'
        else: 
            direction = self.rect.left
            direction_str = 'left'
        match type:
            case 'ki_blast':
                return KiBlast(direction, self.rect.centery, direction_str, True)
            case 'kamehame':
                return Kamehame(direction, self.rect.centery+15, direction_str, True)

    def charge_ki(self, charge: bool):
        if self.__player_control and charge:
            if self.__is_transformed:
                self.actual_mana_points = 32
            self.actual_mana_points = 8
            # print(self.__actual_mp, self.__mana_bar.actual_amount)
            if not self.__is_charging and charge:
                if self.__actual_animation != self.__charge_l and self.__actual_animation != self.__charge_r:
                    self.__is_charging = True
                    if self.__is_looking_right:
                        self.change_animation(self.__charge_r)
                    else:
                        self.change_animation(self.__charge_l)
                    sound = self.__sound_fx[0] if not self.__is_transformed else self.__sound_fx[2]
                    volume = 0.3 if not self.__is_transformed else 0.9
                    self.__sound_player(sound, 'play', volume)
                    self.__move_x = 0
                    self.__move_y = 0
            else: 
                self.__is_charging = False
        else:
            self.__sound_player(self.__sound_fx[0], 'stop', 0.3)
    
    def walk(self, direction: str = 'Right'):
        if self.__player_control:
            match direction:
                case 'Right':
                    look_right = True
                    self.__set_x_animations_preset(self.__speed_walk, self.__walk_r, look_r=look_right)
                case 'Left':
                    look_right = False
                    self.__set_x_animations_preset(-self.__speed_walk, self.__walk_l, look_r=look_right)
    
    def run(self, direction: str = 'Right'):
        if self.__player_control:
            self.__initial_frame = 0
            match direction:
                case 'Right':
                    look_right = True
                    self.__set_x_animations_preset(self.__speed_run, self.__run_r, look_r=look_right)
                case 'Left':
                    look_right = False
                    self.__set_x_animations_preset(-self.__speed_run, self.__run_l, look_r=look_right)
    
    def stay(self):
        if self.__player_control:
            if self.__actual_animation != self.__iddle_l and self.__actual_animation != self.__iddle_r:
                self.change_animation(self.__iddle_r) if self.__is_looking_right else  self.change_animation(self.__iddle_l)
                self.__move_x = 0
                self.__move_y = 0
    
    def jump(self):
        if self.__player_control:
            if(not self.__is_jumping):
                if self.__actual_animation != self.__jump_l and self.__actual_animation != self.__jump_r:
                    self.__is_jumping = True
                    self.__gravity_vel_y = -self.__jump_power
                    if(self.__is_looking_right):
                        self.change_animation(self.__jump_r)
                    else:
                        self.change_animation(self.__jump_l)
    
    def shoot_ki_blast(self):
        if self.__player_control:
            if self.__cooldown_ready_to_action():
                if self.__check_can_shoot('ki_blast'):
                    self.actual_mana_points = -self.__ki_blast_energy_cost
                    print('!iiiaaaaah!!!!')
                    self.__sound_player(self.__sound_fx[1], 'play', 0.25)
                    self.__bullet_group.add(self.__create_ki_power())
                    self.__ki_blast_time = pg.time.get_ticks()
                    
                    if self.__actual_animation != self.__ki_blast_l and self.__actual_animation != self.__ki_blast_r:
                        if self.__is_looking_right:
                            self.change_animation(self.__ki_blast_r)
                        else:
                            self.change_animation(self.__ki_blast_l)
    
    def shoot(self):
        if self.__player_control:
            if not self.__is_transformed:
                self.shoot_ki_blast()
            else:
                if self.__check_can_shoot('super'):
                    if not self.__is_charging_kame and not self.__is_shooting_kame:
                        if self.__cooldown_charge_super():
                            self.__is_charging_kame = True
                            self.__kame_charge_time = pg.time.get_ticks()
                            self.__kame_charge_init_time = pg.time.get_ticks()
                            self.__sound_player(self.__sound_fx[3], 'play', 1)
                            print('!KAAA MEEE HAAA MEEE...')
                            if self.__actual_animation != self.__charge_special_l and self.__actual_animation != self.__charge_special_r:
                                if self.__is_looking_right:
                                    self.change_animation(self.__charge_special_r)
                                else:
                                    self.change_animation(self.__charge_special_l)

                    else:
                        if self.__is_charging_kame and self.__check_is_fully_charged() and not self.__is_shooting_kame:
                            self.__is_charging_kame = False
                            self.__is_shooting_kame = True
                            self.__kame_shoot_init_time = pg.time.get_ticks()
                            self.__kame_shoot_time = pg.time.get_ticks()
                            self.__sound_player(self.__sound_fx[4], 'play', 0.8)
                            if self.__actual_animation != self.__shoot_special_l and self.__actual_animation != self.__shoot_special_r:
                                if self.__is_looking_right:
                                    self.change_animation(self.__shoot_special_r)
                                else:
                                    self.change_animation(self.__shoot_special_l)
                            self.shoot_super()
                        elif self.__check_finish_super():
                            self.__is_shooting_kame = False

    def shoot_super(self):
        if self.__player_control:
            print('!HAAAAA!!!!')
            self.__bullet_group.add(self.__create_ki_power('kamehame'))
            self.actual_mana_points = -self.__kame_energy_cost
            self.__kame_shoot_time = pg.time.get_ticks()

    
    def __check_is_fully_charged(self):
        current_time = pg.time.get_ticks()
        ready_to_shoot = current_time - self.__kame_charge_init_time >= self.__kame_fully_charged_time
        return self.__is_charging_kame and ready_to_shoot

    def __check_finish_super(self):
        current_time = pg.time.get_ticks()
        ready_to_shoot = current_time - self.__kame_shoot_init_time >= 9000
        return self.__is_shooting_kame and ready_to_shoot

    def __set_base_sprites(self):
        self.__iddle_base_r = sf.get_surface_from_spritesheet('./assets/img/player/base/iddle/iddle.png', 3, 1)
        self.__iddle_base_l = sf.get_surface_from_spritesheet('./assets/img/player/base/iddle/iddle.png', 3, 1, flip=True)
        self.__charge_base_r = sf.get_surface_from_spritesheet('./assets/img/player/base/charge/charge.png', 3, 1)
        self.__charge_base_l = sf.get_surface_from_spritesheet('./assets/img/player/base/charge/charge.png', 3, 1, flip=True)
        self.__iddle_r = sf.get_surface_from_spritesheet('./assets/img/player/ssj_1/iddle/iddle.png', 3, 1)
        self.__iddle_l = sf.get_surface_from_spritesheet('./assets/img/player/ssj_1/iddle/iddle.png', 3, 1, flip=True)
        self.__walk_r = sf.get_surface_from_spritesheet('./assets/img/player/ssj_1/walk/walk.png', 3, 1)
        self.__walk_l = sf.get_surface_from_spritesheet('./assets/img/player/ssj_1/walk/walk.png', 3, 1, flip=True)
        self.__run_r = sf.get_surface_from_spritesheet('./assets/img/player/ssj_1/run/run.png', 3, 1)
        self.__run_l = sf.get_surface_from_spritesheet('./assets/img/player/ssj_1/run/run.png', 3, 1, flip=True)
        self.__jump_r = sf.get_surface_from_spritesheet('./assets/img/player/ssj_1/jump/jump.png', 3, 1)
        self.__jump_l = sf.get_surface_from_spritesheet('./assets/img/player/ssj_1/jump/jump.png', 3, 1, flip=True)
        self.__ki_blast_r = sf.get_surface_from_spritesheet('./assets/img/player/ssj_1/attack/attack.png', 11, 1)
        self.__ki_blast_l = sf.get_surface_from_spritesheet('./assets/img/player/ssj_1/attack/attack.png', 11, 1, flip=True)
        self.__charge_r = sf.get_surface_from_spritesheet('./assets/img/player/ssj_1/charge/charge.png', 3, 1)
        self.__charge_l = sf.get_surface_from_spritesheet('./assets/img/player/ssj_1/charge/charge.png', 3, 1, flip=True)

    def __set_transform_sprites(self):
        self.__iddle_r = sf.get_surface_from_spritesheet('./assets/img/player/ssj_2/iddle/iddle.png', 3, 1)
        self.__iddle_l = sf.get_surface_from_spritesheet('./assets/img/player/ssj_2/iddle/iddle.png', 3, 1, flip=True)
        self.__walk_r = sf.get_surface_from_spritesheet('./assets/img/player/ssj_2/walk/walk.png', 3, 1)
        self.__walk_l = sf.get_surface_from_spritesheet('./assets/img/player/ssj_2/walk/walk.png', 3, 1, flip=True)
        self.__run_r = sf.get_surface_from_spritesheet('./assets/img/player/ssj_2/run/run.png', 3, 1)
        self.__run_l = sf.get_surface_from_spritesheet('./assets/img/player/ssj_2/run/run.png', 3, 1, flip=True)
        self.__jump_r = sf.get_surface_from_spritesheet('./assets/img/player/ssj_2/jump/jump.png', 3, 1)
        self.__jump_l = sf.get_surface_from_spritesheet('./assets/img/player/ssj_2/jump/jump.png', 3, 1, flip=True)
        self.__ki_blast_r = sf.get_surface_from_spritesheet('./assets/img/player/ssj_2/attack/attack.png', 2, 1)
        self.__ki_blast_l = sf.get_surface_from_spritesheet('./assets/img/player/ssj_2/attack/attack.png', 2, 1, flip=True)
        self.__charge_r = sf.get_surface_from_spritesheet('./assets/img/player/ssj_2/charge/charge.png', 3, 1)
        self.__charge_l = sf.get_surface_from_spritesheet('./assets/img/player/ssj_2/charge/charge.png', 3, 1, flip=True)
        self.__charge_special_r = sf.get_surface_from_spritesheet('./assets/img/player/ssj_2/attack_special/charge_kame.png', 3, 1)
        self.__charge_special_l = sf.get_surface_from_spritesheet('./assets/img/player/ssj_2/attack_special/charge_kame.png', 3, 1, flip=True)
        self.__shoot_special_r = sf.get_surface_from_spritesheet('./assets/img/player/ssj_2/attack_special/shoot_kame.png', 1, 1)
        self.__shoot_special_l = sf.get_surface_from_spritesheet('./assets/img/player/ssj_2/attack_special/shoot_kame.png', 1, 1, flip=True)

    def events_handler(self, lista_teclas_presionadas, lista_teclado_un_click):
        # for event in lista_teclado_un_click:
        #     match event.type:
        #         case pg.KEYDOWN:
        #             if event.key == pg.K_e:
        #                 self.shoot_ki_blast()
        #                 break
                    # print('Estoy CERRANDO el JUEGO')
                    # self.__executing = False
        
        if lista_teclas_presionadas[pg.K_RIGHT] and not lista_teclas_presionadas[pg.K_LEFT] and not lista_teclas_presionadas[pg.K_r]:
            self.walk('Right')
        if lista_teclas_presionadas[pg.K_LEFT] and not lista_teclas_presionadas[pg.K_RIGHT] and not lista_teclas_presionadas[pg.K_r]:
            self.walk('Left')
        if not lista_teclas_presionadas[pg.K_RIGHT] and not lista_teclas_presionadas[pg.K_LEFT] and not lista_teclas_presionadas[pg.K_r]  and not lista_teclas_presionadas[pg.K_e]:
            self.stay()
        
        if lista_teclas_presionadas[pg.K_RIGHT] and lista_teclas_presionadas[pg.K_LSHIFT] and not lista_teclas_presionadas[pg.K_LEFT] and not lista_teclas_presionadas[pg.K_r]:
            self.run('Right')
        if lista_teclas_presionadas[pg.K_LEFT] and lista_teclas_presionadas[pg.K_LSHIFT] and not lista_teclas_presionadas[pg.K_RIGHT] and not lista_teclas_presionadas[pg.K_r]:
            self.run('Left')
        if lista_teclas_presionadas[pg.K_SPACE] and not lista_teclas_presionadas[pg.K_r]:
            self.jump()
        if lista_teclas_presionadas[pg.K_e] and not lista_teclas_presionadas[pg.K_r]:
            self.shoot()
        if not lista_teclas_presionadas[pg.K_e]:
            self.mute_sounds('charge_kame')
        if lista_teclas_presionadas[pg.K_1]:
            print(f'Cantidad de puntos: {self.puntaje} puntos')
        
        if lista_teclas_presionadas[pg.K_r]:
            self.charge_ki(True)
        if not lista_teclas_presionadas[pg.K_r]:
            self.charge_ki(False)
            self.mute_sounds('charge')
    
    def do_transformation(self):
        self.__set_transform_sprites()
        self.__is_charging = False
        self.__is_transformed = True
        self.__actual_hp = 5000
        self.__life_bar = BarraVida(self.__main_screen_surface, self.__max_hp_by_level, self.__actual_hp, 100, 5 , self.rect.centerx+50, self.rect.y -80, 'hp')
        self.__mana_bar = BarraVida(self.__main_screen_surface, self.__max_mp_by_level, self.__actual_mp, 100, 5 , self.rect.centerx+50, self.rect.y -20, 'mp')
    
    def change_animation(self, nueva_animacion: list[pg.surface.Surface]):
        self.__actual_animation = nueva_animacion
        if self.__initial_frame > 0:
            self.__initial_frame = 0
        self.__actual_img_animation = self.__actual_animation[self.__initial_frame]

    def draw(self, screen: pg.surface.Surface):
        if DEBUG:
            pg.draw.rect(screen, 'red', self.rect)
            #pg.draw.rect(screen, 'green', self.rect.bottom)
        self.__actual_img_animation = self.__actual_animation[self.__initial_frame]
        screen.blit(self.__actual_img_animation, self.rect)

    def update(self, delta_ms, screen: pg.surface.Surface, lista_teclas_presionadas, lista_teclado_un_click, floor_y_coord):
        self.__initial_transform(delta_ms)
        self.events_handler(lista_teclas_presionadas, lista_teclado_un_click)
        self.do_movement(delta_ms, floor_y_coord)
        self.do_animation(delta_ms)
        # self.recharge()
        self.add_gravity()
        self.__life_bar.update(screen, self.rect.x -2, self.rect.y-15, self.__life_bar.actual_amount)
        self.__mana_bar.update(screen, self.rect.x -2, self.rect.y-10, self.__mana_bar.actual_amount)
        self.__bullet_group.update(screen)
        self.draw(screen)
    
    