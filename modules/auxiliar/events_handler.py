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
import sys

from modules.models.player import Player
from modules.auxiliar.common_variables import LOOKING_L, LOOKING_R


def __handler_quit(event):
    """
    If the event type is pg.QUIT, then quit the game and exit the program
    
    :param event: The event that was triggered
    """
    if event.type == pg.QUIT:
        pg.quit()
        sys.exit()


def __handler_key_down(event, player: Player):
    """
    If the right arrow key is pressed, the player will walk right. If the left arrow key is pressed, the
    player will walk left
    
    :param event: The event that was triggered
    :param player: Player
    :type player: Player
    """
    # if event.key == pg.K_RIGHT:
    #     player.walk(LOOKING_R)
    # if event.key == pg.K_LEFT:
    #     player.walk(LOOKING_L)
    if event.key == pg.K_SPACE:
        player.jump()
    # if event.key == pg.K_LCTRL:
    #     player.run(LOOKING_L)
    # if event.key == pg.K_RCTRL:
    #     player.run(LOOKING_R)
    


def __handler_key_up(event, player: Player):
    """
    If the player is walking right or left, stop walking
    
    :param event: The event that was triggered
    :param player: Player
    :type player: Player
    """
    if event.key == pg.K_SPACE:# or event.key == pg.K_RIGHT or event.key == pg.K_LEFT:
        player.stay()


def __handler_keys(event, player: Player):
    """
    If the event is a keydown, then call the handler_key_down function, if the event is a keyup, then
    call the handler_key_up function
    
    :param event: The event that was triggered
    :param player: Player
    :type player: Player
    """
    if event.type == pg.KEYDOWN:
        __handler_key_down(event, player)
    if event.type == pg.KEYUP:
        __handler_key_up(event, player)


def events_handler(player: Player):
    """
    It takes a player object and loops through all the events in the event queue. 
    If the event is a quit event, it calls the handler_quit function. 
    If the event is a keydown event, it calls the handler_keydown function. 
    If the event is a keyup event, it calls the handler_keyup function. 
    If the event is a mouse motion event, it calls the handler_mouse_motion function. 
    If the event is a mouse button down event, it calls the handler_mouse_button_down function. 
    If the event is a mouse button up event, it calls the handler_mouse_button_up function. 
    If the event is a mouse wheel event, it calls the handler_mouse_wheel function. 
    If the event is a joystick axis motion event, it calls the handler_joystick_axis_motion function.
    
    :param player: The main player that makes actions bassed on the user events
    """
    for event in pg.event.get():
        __handler_quit(event)
        __handler_keys(event, player)
    keys = pg.key.get_pressed()
    if keys[pg.K_LEFT] and not keys[pg.K_RIGHT]:
        player.walk(LOOKING_L)
    if keys[pg.K_RIGHT] and not keys[pg.K_LEFT]:
        player.walk(LOOKING_R)
    
    if keys[pg.K_RIGHT] and keys[pg.K_LCTRL] and not keys[pg.K_LEFT]:
        player.run(LOOKING_R)
    if keys[pg.K_LEFT] and keys[pg.K_LCTRL] and not keys[pg.K_RIGHT]:
        player.run(LOOKING_L)
    
    # if keys[pg.K_LCTRL] and not keys[pg.K_RCTRL]:
    #     player.run(LOOKING_L)
    # if keys[pg.K_RCTRL] and not keys[pg.K_LCTRL]:
    #     player.run(LOOKING_R)
    
    if not keys[pg.K_LEFT] and not keys[pg.K_RIGHT] and not keys[pg.K_e] and not keys[pg.K_SPACE]:
        player.stay()
    if keys[pg.K_e]:
        player.attack()
    