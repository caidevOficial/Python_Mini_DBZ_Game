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
from models.constants import ANCHO_VENTANA
from models.surface_manager import SurfaceManager as sf

class KiBlast(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y, direction, img_path = False):
        super().__init__()
        self.direction = direction
        self.__load_img(img_path)
        self.rect = self.image.get_rect(center=(pos_x, pos_y))

    def __load_img(self, img_path: bool):
        if img_path:
            if self.direction == 'right':
                self.image = sf.get_surface_from_spritesheet('./assets/img/blast/ki_blast.png', 1, 1)[0]
            else: self.image = sf.get_surface_from_spritesheet('./assets/img/blast/ki_blast.png', 1, 1, flip=True)[0]
        else: 
            self.image = pg.Surface((20, 20))
            self.image.fill('red')

    def update(self, screen: pg.surface.Surface):
        
        match self.direction:
            case 'right':
                self.rect.x += 15
                if self.rect.x >= ANCHO_VENTANA:
                    self.kill()
            case 'left':
                self.rect.x -= 15
                if self.rect.x <= 0:
                    self.kill()
        self.draw(screen)
        
    def draw(self, screen: pg.surface.Surface):
        screen.blit(self.image, self.rect)