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
from models.surface_manager import SurfaceManager as sf

class Explotion(pg.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self._actual_frame = 0
        self.__actual_animation = sf.get_surface_from_spritesheet('./assets/img/blast/explotion_blast.png', 8, 1, scale_2x=True)
        self.image = self.__actual_animation[self._actual_frame]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.__frame_rate = 35
        self.__update_time = pg.time.get_ticks()
    
    def update(self, screen: pg.surface.Surface):
        current_time = pg.time.get_ticks()
        if current_time - self.__update_time > self.__frame_rate:
            self.__update_time = current_time
            self._actual_frame += 1
            if self._actual_frame == len(self.__actual_animation)-1:
                self.kill()
            else:
                center = self.rect.center
                self.image = self.__actual_animation[self._actual_frame]
                self.rect = self.image.get_rect()
                self.rect.center = center
        self.draw(screen)
    
    def draw(self, screen: pg.surface.Surface):
        self.image = self.__actual_animation[self._actual_frame]
        screen.blit(self.image, self.rect)