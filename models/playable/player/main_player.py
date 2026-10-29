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
from models.constants import ANCHO_VENTANA, debug
from models.hit_points.class_vida import BarraVida
from models.playable.player.metricas import Metrics
from models.blasts.ki_blast import KiBlast
from models.blasts.kamehame import Kamehame
import pygame.mixer as mixer


class Player:

    def __init__(self, screen: pg.surface.Surface, coord_x, coord_y, frame_rate = 100, speed_walk = 5, speed_run = 10, gravity = 0.85, jump = 15.5):
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

        # Registro del manifiesto de animaciones para Lazy Loading
        self.__animation_manifest: dict[str, dict] = {}
        self.__set_base_sprites()

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

        # Normalización de velocidad para movimiento suave por frame
        self.__speed_walk = speed_walk * 0.25 if speed_walk > 10 else speed_walk
        self.__speed_run = speed_run * 0.25 if speed_run > 15 else speed_run

        self.__frame_rate = frame_rate
        self.__player_animation_time = 0

        # Parámetros físicos calibrados para 60 FPS
        self.__gravity = gravity
        self.__jump_power = jump
        self.__terminal_velocity = 14.0
        self.__vel_y = 0.0
        self.__pos_y = float(coord_y)
        self.__is_grounded = True
        self.__is_jumping = False
        self.__is_falling = False

        self.__initial_frame = 0
        # Carga diferida: se obtiene únicamente la animación inicial de reposo
        self.__actual_animation = self.__iddle_base_r
        self.__actual_img_animation = self.__actual_animation[self.__initial_frame]
        self.rect = self.__actual_img_animation.get_rect()
        self.rect.x = coord_x
        self.rect.y = coord_y
        self.__pos_y = float(coord_y)

        self.__bullet_group = pg.sprite.Group()
        self.__puntaje = 0
        self.__metrics.score_gained = 0
        self.__ki_blast_damage = 50
        self.__kame_damage = 5000
        self.__ki_blast_time = 0
        self.__ki_blast_cooldown = 250
        self.__ki_blast_energy_cost = 20
        self.__is_looking_right = True
        self.__is_charging = False
        self.__is_transformed = False
        self.__is_charging_kame = False
        self.__is_shooting_kame = False
        self.__kame_charge_time = 0
        self.__kame_charge_init_time = 0
        self.__kame_shoot_time = 0
        self.__kame_shoot_init_time = 0
        self.__kame_energy_cost = 1500
        self.__kame_fully_charged_time = 10594
        self.__kame_recovery_time = 1200
        self.__kame_shoot_cooldown = 3000

    def __getattr__(self, name: str):
        """
        Lazy loading transparente para las animaciones del jugador.
        Carga el spritesheet bajo demanda únicamente la primera vez que se consulta.
        """
        prefix = f"_{self.__class__.__name__}__"
        if name.startswith(prefix):
            anim_key = name[len(prefix):]
            if anim_key in self.__animation_manifest:
                config = self.__animation_manifest[anim_key]
                loaded_anim = sf.get_surface_from_spritesheet(
                    img_path=config['path'],
                    cols=config['cols'],
                    rows=config['rows'],
                    flip=config.get('flip', False),
                    scale_2x=config.get('scale_2x', True)
                )
                setattr(self, name, loaded_anim)
                return loaded_anim
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    @property
    def actual_hit_points(self):
        return self.__actual_hp

    @actual_hit_points.setter
    def actual_hit_points(self, hit_points):
        if hit_points > 0:
            self.__actual_hp = min(self.__max_hp_by_level, self.__actual_hp + hit_points)
        elif hit_points < 0:
            self.__actual_hp = max(0, self.__actual_hp + hit_points)
        if hasattr(self, '_Player__life_bar') and self.__life_bar is not None:
            self.__life_bar.actual_amount = self.__actual_hp

    @property
    def max_hit_points(self):
        return self.__max_hp_by_level

    @max_hit_points.setter
    def max_hit_points(self, max_hp):
        self.__max_hp_by_level = max_hp
        if hasattr(self, '_Player__life_bar') and self.__life_bar is not None:
            self.__life_bar.max_amount = max_hp

    @property
    def actual_mana_points(self):
        return self.__actual_mp

    @actual_mana_points.setter
    def actual_mana_points(self, mana_points):
        if mana_points > 0:
            self.__actual_mp = min(self.__max_mp_by_level, self.__actual_mp + mana_points)
        elif mana_points < 0:
            self.__actual_mp = max(0, self.__actual_mp + mana_points)
        if hasattr(self, '_Player__mana_bar') and self.__mana_bar is not None:
            self.__mana_bar.actual_amount = self.__actual_mp
        if debug.get('actual_status'):
            print(f'MP: {self.__actual_mp}/{self.__max_mp_by_level}')

    @property
    def max_mana_points(self):
        return self.__max_mp_by_level

    @max_mana_points.setter
    def max_mana_points(self, max_mp):
        self.__max_mp_by_level = max_mp
        if hasattr(self, '_Player__mana_bar') and self.__mana_bar is not None:
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
        self.__metrics.score_gained = puntos

    @property
    def get_blasts(self):
        return self.__bullet_group

    @property
    def ki_blast_damage(self) -> int:
        return self.__ki_blast_damage

    @ki_blast_damage.setter
    def ki_blast_damage(self, value: int):
        self.__ki_blast_damage = value

    @property
    def kame_damage(self) -> int:
        return self.__kame_damage

    @kame_damage.setter
    def kame_damage(self, value: int):
        self.__kame_damage = value

    @property
    def is_charging_energy(self) -> bool:
        return self.__is_charging

    @property
    def is_grounded(self) -> bool:
        return self.__is_grounded

    def __check_can_shoot(self, attack_type: str) -> bool:
        attack_cost = 0
        match attack_type:
            case 'ki_blast':
                attack_cost = self.__ki_blast_energy_cost
            case 'super':
                attack_cost = self.__kame_energy_cost
        if debug.get('actual_status'):
            print(f'Attack cost: {attack_cost} | Actual mana points: {self.__actual_mp}')
        return self.__actual_mp >= attack_cost

    def __sound_player(self, sound_name: pg.mixer.Sound, play_stop: str, volume: float):
        match play_stop:
            case 'play':
                sound_name.set_volume(volume)
                sound_name.play()
            case 'stop':
                sound_name.fadeout(1000)

    def __set_x_animations_preset(self, move_x, animation_list: list[pg.surface.Surface], look_r: bool):
        self.__move_x = move_x
        self.__is_looking_right = look_r
        # En el suelo actualizamos la animación; en el aire preservamos la postura de salto
        if self.__is_grounded:
            if self.__actual_animation != animation_list:
                self.change_animation(animation_list)
        else:
            air_anim = self.__jump_r if look_r else self.__jump_l
            if self.__actual_animation != air_anim:
                self.change_animation(air_anim)

    def jump(self):
        """Ejecuta un salto con física parabólica suave y responsiva."""
        if self.__player_control and self.__is_grounded and not self.__is_charging_kame and not self.__is_shooting_kame:
            self.__vel_y = -self.__jump_power
            self.__is_grounded = False
            self.__is_jumping = True
            self.__is_falling = False
            anim = self.__jump_r if self.__is_looking_right else self.__jump_l
            self.change_animation(anim)

    def __land(self):
        """Restaura el estado al tocar suelo o plataforma."""
        was_airborne = not self.__is_grounded
        self.__vel_y = 0.0
        self.__is_grounded = True
        self.__is_jumping = False
        self.__is_falling = False

        if was_airborne:
            if self.__is_charging_kame or self.__is_shooting_kame:
                return
            keys = pg.key.get_pressed()
            if keys[pg.K_RIGHT] and not keys[pg.K_LEFT]:
                self.__is_looking_right = True
                anim = self.__run_r if keys[pg.K_LSHIFT] else self.__walk_r
                self.change_animation(anim)
            elif keys[pg.K_LEFT] and not keys[pg.K_RIGHT]:
                self.__is_looking_right = False
                anim = self.__run_l if keys[pg.K_LSHIFT] else self.__walk_l
                self.change_animation(anim)
            else:
                anim = self.__iddle_r if self.__is_looking_right else self.__iddle_l
                self.change_animation(anim)

    def __set_borders_limits(self):
        pixels_move = 0
        img_width = self.__actual_img_animation.get_width()
        if self.__move_x > 0:
            pixels_move = self.__move_x if self.rect.x < ANCHO_VENTANA - img_width else 0
        elif self.__move_x < 0:
            pixels_move = self.__move_x if self.rect.x > 0 else 0
        return pixels_move

    def do_movement(self, delta_ms, floor_y_coord, platforms=None):
        if not self.__player_control:
            return

        dt_factor = min(delta_ms / 16.667, 2.0) if delta_ms > 0 else 1.0

        # 1. Movimiento horizontal suave
        if self.__is_charging_kame or self.__is_shooting_kame:
            self.__move_x = 0
        move_x = self.__set_borders_limits()
        self.rect.x += int(move_x * dt_factor)

        # 2. Aceleración por gravedad en velocidad vertical
        self.__vel_y += self.__gravity * dt_factor
        if self.__vel_y > self.__terminal_velocity:
            self.__vel_y = self.__terminal_velocity

        # 3. Integración vertical continua
        prev_bottom = self.rect.bottom
        self.__pos_y += self.__vel_y * dt_factor
        self.rect.y = round(self.__pos_y)

        # 4. Transiciones de estados en el aire
        if self.__vel_y < -1.5:
            self.__is_jumping = True
            self.__is_falling = False
        elif self.__vel_y > 1.5:
            self.__is_jumping = False
            self.__is_falling = True

        # 5. Colisión con plataformas semi-sólidas al descender
        landed = False
        if platforms and self.__vel_y >= 0:
            for plat in platforms:
                if self.rect.right > plat.rect.left + 15 and self.rect.left < plat.rect.right - 15:
                    if prev_bottom <= plat.rect.top + 12 and self.rect.bottom >= plat.rect.top:
                        self.rect.bottom = plat.rect.top
                        self.__pos_y = float(self.rect.y)
                        self.__land()
                        landed = True
                        break

        # 6. Colisión con el nivel del suelo base
        if not landed and floor_y_coord and floor_y_coord > 50:
            if self.rect.bottom >= floor_y_coord:
                self.rect.bottom = floor_y_coord
                self.__pos_y = float(self.rect.y)
                self.__land()
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

    def __cooldown_ready_to_action(self) -> bool:
        current_time = pg.time.get_ticks()
        return self.__ki_blast_time == 0 or current_time - self.__ki_blast_time >= self.__ki_blast_cooldown

    def __cooldown_charge_super(self) -> bool:
        return self.__cooldown_shoot_super()

    def __cooldown_shoot_super(self) -> bool:
        current_time = pg.time.get_ticks()
        return self.__kame_shoot_time == 0 or current_time - self.__kame_shoot_time >= self.__kame_shoot_cooldown

    def mute_sounds(self, sound_type: str) -> None:
        match sound_type:
            case 'charge_kame':
                if self.__is_transformed:
                    self.__sound_fx[3].fadeout(500)
            case 'charge':
                self.__sound_fx[0].fadeout(500)
                self.__sound_fx[2].fadeout(500)

    def initial_config(self, max_hp, max_mp, ki_blast_damage = None, kame_damage = None):
        self.__max_hp_by_level = max_hp
        self.__max_mp_by_level = max_mp
        self.__actual_hp = max_hp
        self.__actual_mp = max_mp
        if ki_blast_damage is not None:
            self.__ki_blast_damage = ki_blast_damage
        if kame_damage is not None:
            self.__kame_damage = kame_damage
        self.__life_bar = BarraVida(self.__main_screen_surface, self.__max_hp_by_level, self.__actual_hp, 100, 5, self.rect.centerx + 50, self.rect.y - 80, 'hp')
        self.__mana_bar = BarraVida(self.__main_screen_surface, self.__max_mp_by_level, self.__actual_mp, 100, 5, self.rect.centerx + 50, self.rect.y - 20, 'mp')

    def initial_level_coords(self, coord_x: int, coord_y: int) -> None:
        self.rect.x = coord_x
        self.rect.y = coord_y
        self.__pos_y = float(coord_y)
        self.__vel_y = 0.0
        self.__is_grounded = True
        self.__is_jumping = False
        self.__is_falling = False
        self.__is_charging_kame = False
        self.__is_shooting_kame = False

    def __initial_transform(self, delta_ms: int):
        current_time = pg.time.get_ticks()
        if not self.__player_control:
            if self.__is_base_state and not self.__is_base_transforming:
                if current_time >= self.__time_until_initial_transform_c and current_time < self.__time_until_initial_transform_c2:
                    self.change_animation(self.__charge_base_r)
                    self.__is_base_transforming = True
                    self.__sound_player(self.__sound_fx[5], 'play', 0.3)
                    if debug.get('actual_status'): print(f'1° IF: current time: {current_time} | delta: {delta_ms} | transf: {self.__is_base_transforming}')
            elif self.__is_base_state and self.__is_base_transforming:
                if current_time >= self.__time_until_initial_transform_c2:
                    self.change_animation(self.__charge_r)
                    self.__is_base_state = False
                    if debug.get('actual_status'): print(f'2° IF: current time: {current_time} | delta: {delta_ms} | base: {self.__is_base_state}')
            elif not self.__is_base_state and self.__is_base_transforming:
                if current_time >= self.__time_until_control:
                    self.change_animation(self.__iddle_r)
                    self.__is_base_transforming = False
                    self.__player_control = True
                    if debug.get('actual_status'): print(f'3° IF: current time: {current_time} | delta: {delta_ms} | control: {self.__player_control}')
        else:
            self.__sound_player(self.__sound_fx[5], 'stop', 0.3)

    #! ACCIONES
    def __create_ki_power(self, attack_type: str = 'ki_blast'):
        if self.__is_looking_right:
            direction = self.rect.right
            direction_str = 'right'
        else:
            direction = self.rect.left
            direction_str = 'left'
        match attack_type:
            case 'ki_blast':
                return KiBlast(direction, self.rect.centery, direction_str, True, damage=self.__ki_blast_damage)
            case 'kamehame':
                return Kamehame(direction, self.rect.centery + 15, direction_str, True, damage=self.__kame_damage)
    
    def is_charging_kame(self) -> bool:
        return self.__is_charging_kame

    def is_shooting_kame(self) -> bool:
        return self.__is_shooting_kame

    def cancel_charge_kame(self):
        """Cancela la carga del Kamehameha si se suelta la tecla antes de tiempo."""
        if self.__is_charging_kame:
            self.__is_charging_kame = False
            self.mute_sounds('charge_kame')
            if self.__actual_animation in (self.__charge_special_l, self.__charge_special_r):
                self.stay()

    def charge_ki(self, charge: bool):
        if self.__player_control and charge and not self.__is_charging_kame and not self.__is_shooting_kame:
            if self.__is_transformed:
                self.actual_mana_points = 32
            else:
                self.actual_mana_points = 8

            if not self.__is_charging:
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
            else:
                pass
        else:
            if self.__is_charging:
                self.__is_charging = False
            self.__sound_player(self.__sound_fx[0], 'stop', 0.3)

    def walk(self, direction: str = 'Right'):
        if self.__player_control and not self.__is_charging_kame and not self.__is_shooting_kame:
            match direction:
                case 'Right':
                    self.__set_x_animations_preset(self.__speed_walk, self.__walk_r, look_r=True)
                case 'Left':
                    self.__set_x_animations_preset(-self.__speed_walk, self.__walk_l, look_r=False)

    def run(self, direction: str = 'Right'):
        if self.__player_control and not self.__is_charging_kame and not self.__is_shooting_kame:
            match direction:
                case 'Right':
                    self.__set_x_animations_preset(self.__speed_run, self.__run_r, look_r=True)
                case 'Left':
                    self.__set_x_animations_preset(-self.__speed_run, self.__run_l, look_r=False)

    def stay(self):
        if self.__player_control and not self.__is_charging_kame and not self.__is_shooting_kame:
            self.__move_x = 0
            # Solo restaurar idle si estamos tocando el suelo
            if self.__is_grounded:
                if self.__actual_animation not in (self.__iddle_l, self.__iddle_r):
                    self.change_animation(self.__iddle_r if self.__is_looking_right else self.__iddle_l)
            else:
                air_anim = self.__jump_r if self.__is_looking_right else self.__jump_l
                if self.__actual_animation != air_anim:
                    self.change_animation(air_anim)

    def shoot_ki_blast(self):
        if self.__player_control:
            if self.__cooldown_ready_to_action():
                if self.__check_can_shoot('ki_blast'):
                    self.actual_mana_points = -self.__ki_blast_energy_cost
                    self.__sound_player(self.__sound_fx[1], 'play', 0.25)
                    self.__bullet_group.add(self.__create_ki_power('ki_blast'))
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
                if self.__is_shooting_kame:
                    return
                if self.__check_can_shoot('super'):
                    if not self.__is_charging_kame:
                        if self.__cooldown_charge_super():
                            self.__is_charging_kame = True
                            self.__kame_charge_time = pg.time.get_ticks()
                            self.__kame_charge_init_time = pg.time.get_ticks()
                            self.__sound_player(self.__sound_fx[3], 'play', 1)
                            if self.__actual_animation != self.__charge_special_l and self.__actual_animation != self.__charge_special_r:
                                if self.__is_looking_right:
                                    self.change_animation(self.__charge_special_r)
                                else:
                                    self.change_animation(self.__charge_special_l)
                    else:
                        if self.__check_is_fully_charged():
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

    def shoot_super(self):
        if self.__player_control:
            self.__bullet_group.add(self.__create_ki_power('kamehame'))
            self.actual_mana_points = -self.__kame_energy_cost
            self.__kame_shoot_time = pg.time.get_ticks()

    def __check_is_fully_charged(self):
        current_time = pg.time.get_ticks()
        ready_to_shoot = current_time - self.__kame_charge_init_time >= self.__kame_fully_charged_time
        return self.__is_charging_kame and ready_to_shoot

    def __check_finish_super(self):
        if self.__is_shooting_kame:
            current_time = pg.time.get_ticks()
            if current_time - self.__kame_shoot_init_time >= self.__kame_recovery_time:
                self.__is_shooting_kame = False
                self.stay()

    def __set_base_sprites(self):
        """Registra el manifiesto de animaciones del estado base y SSJ1 para carga bajo demanda."""
        self.__animation_manifest.update({
            'iddle_base_r': {'path': './assets/img/player/base/iddle/iddle.png', 'cols': 3, 'rows': 1, 'flip': False},
            'iddle_base_l': {'path': './assets/img/player/base/iddle/iddle.png', 'cols': 3, 'rows': 1, 'flip': True},
            'charge_base_r': {'path': './assets/img/player/base/charge/charge.png', 'cols': 3, 'rows': 1, 'flip': False},
            'charge_base_l': {'path': './assets/img/player/base/charge/charge.png', 'cols': 3, 'rows': 1, 'flip': True},
            'iddle_r': {'path': './assets/img/player/ssj_1/iddle/iddle.png', 'cols': 3, 'rows': 1, 'flip': False},
            'iddle_l': {'path': './assets/img/player/ssj_1/iddle/iddle.png', 'cols': 3, 'rows': 1, 'flip': True},
            'walk_r': {'path': './assets/img/player/ssj_1/walk/walk.png', 'cols': 3, 'rows': 1, 'flip': False},
            'walk_l': {'path': './assets/img/player/ssj_1/walk/walk.png', 'cols': 3, 'rows': 1, 'flip': True},
            'run_r': {'path': './assets/img/player/ssj_1/run/run.png', 'cols': 3, 'rows': 1, 'flip': False},
            'run_l': {'path': './assets/img/player/ssj_1/run/run.png', 'cols': 3, 'rows': 1, 'flip': True},
            'jump_r': {'path': './assets/img/player/ssj_1/jump/jump.png', 'cols': 3, 'rows': 1, 'flip': False},
            'jump_l': {'path': './assets/img/player/ssj_1/jump/jump.png', 'cols': 3, 'rows': 1, 'flip': True},
            'ki_blast_r': {'path': './assets/img/player/ssj_1/attack/attack.png', 'cols': 11, 'rows': 1, 'flip': False},
            'ki_blast_l': {'path': './assets/img/player/ssj_1/attack/attack.png', 'cols': 11, 'rows': 1, 'flip': True},
            'charge_r': {'path': './assets/img/player/ssj_1/charge/charge.png', 'cols': 3, 'rows': 1, 'flip': False},
            'charge_l': {'path': './assets/img/player/ssj_1/charge/charge.png', 'cols': 3, 'rows': 1, 'flip': True},
        })

    def __set_transform_sprites(self):
        """Actualiza el manifiesto a SSJ2 y purga referencias antiguas para lazy loading."""
        ssj2_manifest = {
            'iddle_r': {'path': './assets/img/player/ssj_2/iddle/iddle.png', 'cols': 3, 'rows': 1, 'flip': False},
            'iddle_l': {'path': './assets/img/player/ssj_2/iddle/iddle.png', 'cols': 3, 'rows': 1, 'flip': True},
            'walk_r': {'path': './assets/img/player/ssj_2/walk/walk.png', 'cols': 3, 'rows': 1, 'flip': False},
            'walk_l': {'path': './assets/img/player/ssj_2/walk/walk.png', 'cols': 3, 'rows': 1, 'flip': True},
            'run_r': {'path': './assets/img/player/ssj_2/run/run.png', 'cols': 3, 'rows': 1, 'flip': False},
            'run_l': {'path': './assets/img/player/ssj_2/run/run.png', 'cols': 3, 'rows': 1, 'flip': True},
            'jump_r': {'path': './assets/img/player/ssj_2/jump/jump.png', 'cols': 3, 'rows': 1, 'flip': False},
            'jump_l': {'path': './assets/img/player/ssj_2/jump/jump.png', 'cols': 3, 'rows': 1, 'flip': True},
            'ki_blast_r': {'path': './assets/img/player/ssj_2/attack/attack.png', 'cols': 2, 'rows': 1, 'flip': False},
            'ki_blast_l': {'path': './assets/img/player/ssj_2/attack/attack.png', 'cols': 2, 'rows': 1, 'flip': True},
            'charge_r': {'path': './assets/img/player/ssj_2/charge/charge.png', 'cols': 3, 'rows': 1, 'flip': False},
            'charge_l': {'path': './assets/img/player/ssj_2/charge/charge.png', 'cols': 3, 'rows': 1, 'flip': True},
            'charge_special_r': {'path': './assets/img/player/ssj_2/attack_special/charge_kame.png', 'cols': 3, 'rows': 1, 'flip': False},
            'charge_special_l': {'path': './assets/img/player/ssj_2/attack_special/charge_kame.png', 'cols': 3, 'rows': 1, 'flip': True},
            'shoot_special_r': {'path': './assets/img/player/ssj_2/attack_special/shoot_kame.png', 'cols': 1, 'rows': 1, 'flip': False},
            'shoot_special_l': {'path': './assets/img/player/ssj_2/attack_special/shoot_kame.png', 'cols': 1, 'rows': 1, 'flip': True},
        }
        self.__animation_manifest.update(ssj2_manifest)

        prefix = f"_{self.__class__.__name__}__"
        for key in ssj2_manifest.keys():
            attr_name = f"{prefix}{key}"
            if attr_name in self.__dict__:
                del self.__dict__[attr_name]

    def events_handler(self, lista_teclas_presionadas, lista_teclado_un_click):
        if lista_teclas_presionadas[pg.K_RIGHT] and not lista_teclas_presionadas[pg.K_LEFT] and not lista_teclas_presionadas[pg.K_r]:
            if lista_teclas_presionadas[pg.K_LSHIFT]:
                self.run('Right')
            else:
                self.walk('Right')

        elif lista_teclas_presionadas[pg.K_LEFT] and not lista_teclas_presionadas[pg.K_RIGHT] and not lista_teclas_presionadas[pg.K_r]:
            if lista_teclas_presionadas[pg.K_LSHIFT]:
                self.run('Left')
            else:
                self.walk('Left')

        elif not lista_teclas_presionadas[pg.K_RIGHT] and not lista_teclas_presionadas[pg.K_LEFT] and not lista_teclas_presionadas[pg.K_r] and not lista_teclas_presionadas[pg.K_e]:
            self.stay()

        if lista_teclas_presionadas[pg.K_SPACE] and not lista_teclas_presionadas[pg.K_r]:
            self.jump()

        if lista_teclas_presionadas[pg.K_e] and not lista_teclas_presionadas[pg.K_r]:
            self.shoot()
        else:
            if self.__is_charging_kame:
                self.cancel_charge_kame()
            else:
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
        self.__life_bar = BarraVida(self.__main_screen_surface, self.__max_hp_by_level, self.__actual_hp, 100, 5, self.rect.centerx + 50, self.rect.y - 80, 'hp')
        self.__mana_bar = BarraVida(self.__main_screen_surface, self.__max_mp_by_level, self.__actual_mp, 100, 5, self.rect.centerx + 50, self.rect.y - 20, 'mp')

    def change_animation(self, nueva_animacion: list[pg.surface.Surface]):
        self.__actual_animation = nueva_animacion
        if self.__initial_frame >= len(self.__actual_animation):
            self.__initial_frame = 0
        self.__actual_img_animation = self.__actual_animation[self.__initial_frame]

    def draw(self, screen: pg.surface.Surface):
        if debug.get('actual_status'):
            pg.draw.rect(screen, 'red', self.rect, 2)
        if self.__initial_frame < len(self.__actual_animation):
            self.__actual_img_animation = self.__actual_animation[self.__initial_frame]
        screen.blit(self.__actual_img_animation, self.rect)

    def update(self, delta_ms, screen: pg.surface.Surface, lista_teclas_presionadas, lista_teclado_un_click, floor_y_coord, platforms=None):
        self.__initial_transform(delta_ms)
        self.__check_finish_super()
        self.events_handler(lista_teclas_presionadas, lista_teclado_un_click)
        self.do_movement(delta_ms, floor_y_coord, platforms)
        self.do_animation(delta_ms)
        self.__life_bar.update(screen, self.rect.x - 2, self.rect.y - 15, self.__actual_hp)
        self.__mana_bar.update(screen, self.rect.x - 2, self.rect.y - 10, self.__actual_mp)
        self.__bullet_group.update(screen)
