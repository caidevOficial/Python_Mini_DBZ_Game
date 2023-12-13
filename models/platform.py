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
from models.constants import GREEN, DEBUG, TRANSPARENT

class Platform(pg.sprite.Sprite):
    def __init__(self, image_path, x_axis, y_axis, width, height):
        super().__init__()
        self.__set_image(width, height, image_path)
        self.rect = self.image.get_rect(topleft=(x_axis, y_axis))

    def __set_image(self, ancho, alto, image_path: str = ''):
        """
        The function sets the image attribute of an object to either a scaled image loaded from a file
        path or a blank surface of a specified size.
        
        :param ancho: The parameter "ancho" represents the width of the image in pixels
        :param alto: The parameter "alto" represents the height of the image in pixels
        :param image_path: The `image_path` parameter is a string that represents the file path of the
        image that you want to load
        :type image_path: str
        """
        if image_path:
            self.image = pg.transform.scale(
                pg.image.load(image_path), (ancho, alto))
        else:
            self.image = pg.surface.Surface(size=(ancho, alto))

    def __debug_platform(self, screen):
        """
        The function draws a green rectangle with a thickness of 3 on the screen.
        
        :param screen: The "screen" parameter is the surface object representing the game window or
        screen on which the rectangle will be drawn
        """
        pg.draw.rect(screen, (GREEN), self.rect, 3)

    def draw(self, screen):
        """
        The function draws the image of a platform on the screen.
        
        :param screen: The "screen" parameter is the surface on which the image will be drawn. It
        represents the window or screen where the game is being displayed
        """
        if DEBUG: self.__debug_platform(screen)
        screen.blit(self.image, self.rect)

    def update(self, screen: pg.surface.Surface):
        """
        The function updates the screen by drawing the object on it.
        
        :param screen: The "screen" parameter is a pygame surface object that represents the window or
        screen where the game is being displayed
        :type screen: pg.surface.Surface
        """
        self.draw(screen)
