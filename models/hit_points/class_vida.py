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
from models.constants import LIGHT_CYAN, LIGHT_GREEN

class BarraVida:
    def __init__(self, screen: pygame.Surface, vida_maxima: int, vida_actual: int, ancho_bar: int, alto_bar: int, pos_x: int, pos_y: int, type: str) -> None:
        self.x = pos_x
        self.y = pos_y
        self.ancho = ancho_bar
        self.alto = alto_bar
        self.vida_maxima = max(1, vida_maxima)
        self.vida_actual = max(0, min(self.vida_maxima, vida_actual))
        self.screen = screen
        self.__main_color = type

    def draw(self, screen: pygame.Surface) -> None:
        # Fondo rojo
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.ancho, self.alto))
        # Barra frontal según porcentaje actual
        pct = max(0.0, min(1.0, self.vida_actual / self.vida_maxima))
        current_w = int(self.ancho * pct)
        if current_w > 0:
            color = LIGHT_GREEN if self.__main_color == 'hp' else LIGHT_CYAN
            pygame.draw.rect(screen, color, (self.x, self.y, current_w, self.alto))

    @property
    def actual_amount(self):
        return self.vida_actual

    @actual_amount.setter
    def actual_amount(self, amount):
        self.vida_actual = max(0, min(self.vida_maxima, amount))

    @property
    def max_amount(self):
        return self.vida_maxima

    @max_amount.setter
    def max_amount(self, amount):
        self.vida_maxima = max(1, amount)

    def update(self, screen: pygame.surface.Surface, personaje_rect_x, personaje_rect_y, vida_actual) -> None:
        self.x = personaje_rect_x
        self.y = personaje_rect_y
        self.vida_actual = max(0, min(self.vida_maxima, vida_actual))
        self.draw(screen)
