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

class SurfaceManager:

    @staticmethod
    def get_surface_from_spritesheet(img_path: str, cols: int, rows: int, step = 1, scale_2x: bool = True, dimentions: tuple = None, flip: bool = False) -> list[pg.surface.Surface]:
        sprites_list = list()
        surface_img = pg.image.load(img_path).convert_alpha()
        frame_width = int(surface_img.get_width()/cols)
        frame_height = int(surface_img.get_height()/rows)

        for row in range(rows):

            for column in range(0, cols, step):
                x_axis = column * frame_width
                y_axis = row * frame_height

                frame_surface = surface_img.subsurface(
                    x_axis, y_axis, frame_width, frame_height
                )

                if flip:
                    frame_surface = pg.transform.flip(frame_surface, True, False)
                # opcional para escalar la imagen tamaño x2
                if scale_2x:
                    frame_surface = pg.transform.scale2x(frame_surface)
                if dimentions:
                    frame_surface = pg.transform.scale(frame_surface, dimentions)
                sprites_list.append(frame_surface)
        return sprites_list