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

import pygame

class BarraVida:
    def __init__(self, screen : pygame.Surface, vida_maxima : int, ancho_bar : int, alto_bar: int, pos_x : int, pos_y : int)-> None:
        self.x = pos_x
        self.y = pos_y
        self.ancho = ancho_bar
        self.alto = alto_bar
        self.vida_maxima = vida_maxima
        self.vida_actual = vida_maxima

        self.image = pygame.Surface((self.ancho, self.alto))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.screen = screen
        self.ancho_bar_2 = self.vida_actual * 100 / self.vida_maxima
        self.image_2 = pygame.Surface((self.ancho_bar_2, self.alto))
        self.rect_2 = self.image_2.get_rect()
        self.rect_2.x = pos_x
        self.rect_2.y = pos_y
        self.image_2.fill((0, 255, 0))
        

    def draw(self, screen : pygame.Surface)-> None:
        screen.blit(self.image, self.rect)# rojo - barra de atras
        screen.blit(self.image_2, self.rect) # verde - barra de delante


    def update(self, screen: pygame.surface.Surface, personaje_rect_x, personaje_rect_y, vida_actual)-> None:
        self.rect.x = personaje_rect_x  # Actualiza la posición horizontal
        self.rect.y = personaje_rect_y
        self.ancho_bar_2 = vida_actual * 100 / self.vida_maxima
        if(self.image_2.get_width() > 0):
            self.image_2 = pygame.Surface((self.ancho_bar_2, self.alto))
            self.image_2.fill((0, 255, 0))
        self.draw(screen)
