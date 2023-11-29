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

import json
import pygame as pg
from models.playable.player.main_player import Player
from models.enemy import Enemy
from models.explotion import Explotion

class Stage:

    def __init__(self, screen: pg.surface.Surface, player: Player, limit_w, limit_h, stage_name: str) -> None:
        self.__stage_name = stage_name
        self.__video = None
        self.player_sprite = player  # posicion inicial
        self.__stage_configs = {}
        self.__limit_w = limit_w
        self.__limit_h = limit_h
        self.__main_screen = screen
        self.__win = False
        self.__explotions_group = pg.sprite.Group()
        self.player = pg.sprite.GroupSingle(self.player_sprite)
        self.enemies = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.__get_configs()
        self.__floor_y_coord = self.__stage_configs.get('scenario').get('ground_y_coord_level')

        self.__score_added = False
        
        self.__enemies_coords: list[dict] = self.__stage_configs.get('enemies').get('enemies_coords')
        self.__enemies_configs: dict = self.__stage_configs.get('enemies').get('enemies_configs')
        self.__enemies_amount = self.__stage_configs.get('enemies').get('enemies_amount')
        self.__score_multiplier = self.__stage_configs.get('score_multiplier')
        self.__bgd_img = pg.image.load(self.__stage_configs.get('scenario').get('background'))
        self.__bgd_scaled_img = pg.transform.scale(self.__bgd_img, (self.__limit_w, self.__limit_h))
        self.__player_presets = self.__stage_configs.get('player')
        self.__player_max_hp = self.__player_presets.get('hp')
        self.__player_max_mp = self.__player_presets.get('mp')
        self.__player_coords = self.__player_presets.get('coords')
        self.player_sprite.initial_config(self.__player_max_hp, self.__player_max_mp)
        self.player_sprite.initial_level_coords(self.__player_coords.get('x'), self.__player_coords.get('y'))
        self.__playing_sound = False
        self.__music_stage = pg.mixer.Sound(self.__stage_configs.get('scenario').get('background_music'))
        self.__spawn_enemy()

    @property
    def stage_name(self):
        return self.__stage_name

    @property
    def bkg_img(self) -> pg.surface.Surface:
        return self.__bgd_scaled_img

    def __get_configs(self):
        with open('./configs/config.json', 'r') as configs:
            self.__stage_configs = json.load(configs)[self.__stage_name]
            #print(self.__stage_configs)

    def __spawn_enemy(self):
        for i in range(self.__enemies_amount):
            coord = self.__enemies_coords[i]
            self.enemies.add(
                Enemy(coord.get('x'), coord.get('y'), self.__enemies_configs)
            )

    # def __check_hp_boss(self):
    #     match self.enemies[0]:
    #         case 500:
    #             self.enemies[0].attack_power += self.__multipliers[1].get("multiplicador")

    def check_win(self) -> bool:
        match self.__stage_name:
            case 'stage_1' | 'stage_2' | 'stage_3' | 'stage_4':
                self.__win = len(self.enemies) == 0

    def stage_passed(self):
        if self.__win:
            self.__stop_music()
        return self.__win

    def __asignar_puntajes_a_jugador(self, enemigos_antes: int, enemigos_despues: int):
        if not self.__score_added and enemigos_antes > enemigos_despues:
            self.player_sprite.puntaje += (enemigos_antes - enemigos_despues) * self.__score_multiplier

    def __play_music(self):
        if not self.__playing_sound:
            self.__playing_sound = True
            self.__music_stage.set_volume(0.35)
            if self.__stage_name == 'stage_4':
                self.__music_stage.set_volume(0.15)
            self.__music_stage.play(loops=-1, fade_ms=900)
    
    def __stop_music(self):
        if self.__playing_sound and self.__win:
            self.__playing_sound = False
            self.__music_stage.fadeout(150)

    def __add_explotion(self, enemy_rect: pg.rect.Rect):
        self.__explotions_group.add(
            Explotion(enemy_rect.center, None)
        )

    def __check_collide(self):
        for blast in self.player_sprite.get_blasts:
            cantidad_enemigos_antes = len(self.enemies)
            for enemy in self.enemies:
                if pg.sprite.collide_rect(blast, enemy):
                    self.__add_explotion(enemy.rect)
                    blast.kill()
                    enemy.kill()
                    cantidad_enemigos_despues = len(self.enemies)
                    self.__asignar_puntajes_a_jugador(cantidad_enemigos_antes, cantidad_enemigos_despues)
            
            # pg.sprite.spritecollide(blast, self.enemies, True)
            # if cantidad_enemigos_antes > cantidad_enemigos_despues:
            #     blast.kill()

    def run(self, delta_ms, lista_teclas, lista_teclado_un_click):
        self.enemies.update(delta_ms, self.__main_screen, self.__floor_y_coord)
        self.__explotions_group.update(self.__main_screen)
        self.player.update(delta_ms, self.__main_screen, lista_teclas, lista_teclado_un_click, self.__floor_y_coord)
        self.__check_collide()
        self.__play_music()
        # self.__check_hp_boss()
        self.check_win()
