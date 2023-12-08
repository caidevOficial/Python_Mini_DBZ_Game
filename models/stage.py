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
from models.constantes import (
    ANCHO_VENTANA, ALTO_VENTANA, DBZ_BLACK, 
    TRANSPARENT, DBZ_RED, DBZ_YELLOW, DBZ_ORANGE
)

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
        self.__set_fonts()
        self.__time_left = self.__stage_configs.get('time_seconds')
        self.__actual_time = pg.time.get_ticks()
        self.__time_display = ''

    @property
    def stage_name(self):
        return self.__stage_name

    @property
    def bkg_img(self) -> pg.surface.Surface:
        return self.__bgd_scaled_img

    def __set_fonts(self):
        self.__text_font = pg.font.Font("./assets/fonts/Saiyan-Sans.ttf", 32)
        self.__number_font = pg.font.Font("./assets/fonts/namco.ttf", 18)
        self.__main_font = pg.font.Font("./assets/fonts/Saiyan-Sans.ttf", 64)
        self.__time_text = pg.font.Font("./assets/fonts/Halimount.otf", 32)
        #self.__fuente_negrita_inclinada = pg.font.Font("./assets/fonts/", 72)

    def __render_text(self):
        score_text: pg.surface.Surface = self.__text_font.render('Score: ', True, DBZ_YELLOW)
        score_number = self.__number_font.render(f'{self.player_sprite.puntaje}', True, DBZ_RED)
        tiempo_text = self.__time_text.render(f"Time: {self.__time_display}", True, DBZ_ORANGE)
        width_box = score_text.get_width() + score_number.get_width()
        height_box = max(score_text.get_height(), score_number.get_height())
        
        # Esquina superior izquierda de la caja
        #caja_texto_x = (ANCHO_VENTANA - width_box) // 2
        # caja_texto_y = (ALTO_VENTANA - height_box) // 2
        caja_texto_x = 10
        caja_texto_y = 10

        pg.draw.rect(self.__main_screen, DBZ_BLACK, (caja_texto_x, caja_texto_y, width_box, height_box))

        x1 = caja_texto_x
        y1 = caja_texto_y

        x2 = x1 + score_text.get_width()
        y2 = caja_texto_y + 5

        x3_time = (ANCHO_VENTANA //2 - tiempo_text.get_width() // 2)

        self.__main_screen.blit(score_text, (x1, y1))
        self.__main_screen.blit(score_number, (x2, y2))
        self.__main_screen.blit(tiempo_text, (x3_time, y1))

    def __get_configs(self):
        with open('./configs/config.json', 'r') as configs:
            self.__stage_configs = json.load(configs)[self.__stage_name]

    def __spawn_enemy(self):
        amount = len(self.__enemies_coords)\
            if len(self.__enemies_coords) > self.__enemies_amount\
            else self.__enemies_amount
        for i in range(amount):
            coord = self.__enemies_coords[i]
            self.enemies.add(
                Enemy(coord.get('x'), coord.get('y'), self.__enemies_configs)
            )

    def check_win(self) -> bool:
        match self.__stage_name:
            case 'stage_1' | 'stage_2' | 'stage_3' | 'stage_4':
                self.__win = len(self.enemies) == 0

    def stage_passed(self):
        if self.__win:
            self.__stop_music()
        return self.__win

    def __asignar_puntajes_a_jugador(self, enemy: Enemy):
        print(f'Puntaje: {enemy.enemy_score} | Multiplicador: {self.__score_multiplier}')
        puntaje = enemy.enemy_score * self.__score_multiplier
        print(f'Total a asignar: {puntaje}')
        print(f'Puntaje actual: {self.player_sprite.puntaje}')
        self.player_sprite.puntaje = puntaje
        print(f'Puntaje Nuevo: {self.player_sprite.puntaje}')

    def __play_music(self):
        """
        The function plays music with different volume levels depending on the stage name.
        """
        if not self.__playing_sound:
            self.__playing_sound = True
            self.__music_stage.set_volume(0.35)
            if self.__stage_name == 'stage_4':
                self.__music_stage.set_volume(0.15)
            self.__music_stage.play(loops=-1, fade_ms=900)
    
    def __stop_music(self):
        """
        The function stops the currently playing music by fading it out.
        """
        if self.__playing_sound and self.__win:
            self.__playing_sound = False
            self.__music_stage.fadeout(150)

    def __add_explotion(self, enemy_rect: pg.rect.Rect):
        """
        The function adds an explosion to a group of explosions at the center of an enemy's rectangle.
        
        :param enemy_rect: enemy_rect is a parameter of type pg.rect.Rect. It represents the rectangle
        that defines the position and size of an enemy object
        :type enemy_rect: pg.rect.Rect
        """
        self.__explotions_group.add(
            Explotion(enemy_rect.center)
        )

    def __check_collide(self):
        for blast in self.player_sprite.get_blasts:
            for enemy in self.enemies:
                if pg.sprite.collide_rect(blast, enemy):
                    self.__add_explotion(enemy.rect)
                    self.__asignar_puntajes_a_jugador(enemy)
                    blast.kill()
                    enemy.kill()
            
            # pg.sprite.spritecollide(blast, self.enemies, True)
            # if cantidad_enemigos_antes > cantidad_enemigos_despues:
            #     blast.kill()
    
    def __update_time(self):
        if self.__time_left >= 0:
            current_time = pg.time.get_ticks()
            if current_time - self.__actual_time >= 1000:
                min, sec = divmod(self.__time_left, 60)
                self.__time_display = f'{min:02.0f}:{sec:02.0f}'
                self.__actual_time = current_time
                self.__time_left -= 1

    def run(self, delta_ms, lista_teclas, lista_teclado_un_click):
        self.__update_time()
        self.__render_text()
        self.enemies.update(delta_ms, self.__main_screen, self.__floor_y_coord)
        self.__explotions_group.update(self.__main_screen)
        self.player.update(delta_ms, self.__main_screen, lista_teclas, lista_teclado_un_click, self.__floor_y_coord)
        self.__check_collide()
        self.__play_music()
        # self.__check_hp_boss()
        self.check_win()
