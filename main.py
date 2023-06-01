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
from modules.auxiliar.events_handler import events_handler
from modules.auxiliar.auxiliar import Auxiliar
from modules.auxiliar.common_variables import *
from modules.models.player import Player

game_screen = pg.display.set_mode((WINDOWS_WIDTH, WINDOWS_HEIGHT))
pg.init()
clock = pg.time.Clock()
back_img = pg.image.load(f'{BACKGROUND_IMG}')
back_img = pg.transform.scale(back_img, (WINDOWS_WIDTH, WINDOWS_HEIGHT))
Auxiliar.play_sound()

player1 = Player(0, 0, frame_rate=70, speed_walk=18, speed_run=36)

while True:

    events_handler(player1)

    game_screen.blit(back_img, back_img.get_rect())
    # !TODO: Update player - verify how the player interacts with the stage
    delta_ms = clock.tick(FPS)
    player1.update(delta_ms)
    player1.draw(game_screen)
    # !TODO: Update enemy
    # !TODO: Draw player
    # !TODO: Draw all the stage
    pg.display.flip()
