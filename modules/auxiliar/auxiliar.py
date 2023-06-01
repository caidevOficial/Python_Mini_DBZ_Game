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
import pygame.mixer as mixer
from modules.auxiliar.common_variables import BACKGROUND_MUSIC


class Auxiliar:
    @staticmethod
    def get_surface_from_spritesheet(path: str, cols: int, rows: int, step: int = 1, flip: bool = False) -> list[pg.surface.Surface]:
        """
        It takes a spritesheet image, and returns a list of surfaces, each surface being a frame of the
        spritesheet
        
        :param path: The path to the spritesheet
        :param rows: The number of rows in the spritesheet
        :param cols: number of columns in the spritesheet
        :return: A list of surfaces.
        """
        sprites = list()
        surface_img = pg.image.load(path)
        frame_width = int(surface_img.get_width()/cols)
        frame_height = int(surface_img.get_height()/rows)

        for row in range(rows):
            for column in range(0, cols, step):
                x_axis = column * frame_width
                y_axis = row * frame_height
                # print(x_axis, y_axis, frame_width, frame_height)
                frame_surface = surface_img.subsurface(
                    x_axis, y_axis, frame_width, frame_height)
                if flip:
                    frame_surface = pg.transform.flip(
                        frame_surface, True, False)
                sprites.append(frame_surface)
        return sprites
    
    @staticmethod
    def play_sound() -> None:
        """
        The function plays a background music with a specified volume (0.5).
        """
        sound = mixer.Sound(BACKGROUND_MUSIC)
        mixer.Sound.set_volume(sound, 0.5)
        mixer.Sound.play(sound)
