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

class Metrics:
    def __init__(self) -> None:
        self.__defeated_enemies = 0
        self.__hp_won = 0
        self.__score_gained = 0
        self.__items_obtained = 0

    @property
    def defeated_enemies(self) -> int:
        return self.__defeated_enemies
    
    @defeated_enemies.setter
    def defeated_enemies(self, new_defeated_enemies: int):
        self.__defeated_enemies += new_defeated_enemies
    
    @property
    def hp_won(self) -> int:
        return self.__hp_won
    
    @hp_won.setter
    def hp_won(self, new_hp_won: int):
        self.__hp_won += new_hp_won
    
    @property
    def score_gained(self) -> int:
        return self.__score_gained
    
    @score_gained.setter
    def score_gained(self, new_score_gained: int):
        self.__score_gained += new_score_gained
    
    @property
    def items_obtained(self) -> int:
        return self.__items_obtained
    
    @items_obtained.setter
    def items_obtained(self, new_items_obtained: int):
        self.__items_obtained += new_items_obtained
