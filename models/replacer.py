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

from models.constants import ALTO_VENTANA, ANCHO_VENTANA
import json

class Replacer:
    
    def __init__(self, stage_name: str):
        self.__config_file_path = './configs/config.json'
        self.__configs_replaced = {}
        self.__replace_tokens(stage_name)

    def __replace_tokens(self, stage_name: str):
        """
        The function replaces specific tokens in a JSON file with corresponding values and parses the
        modified JSON file.
        
        :param stage_name: The `stage_name` parameter is a string that represents the name of a stage in
        the configuration file
        :type stage_name: str
        """
        with open(self.__config_file_path, 'r') as config:
            raw_file = str(json.load(config).get(stage_name))
            raw_file = raw_file\
                .replace("'ALTO_VENTANA'", f'{ALTO_VENTANA}')\
                .replace("'ANCHO_VENTANA'", f'{ANCHO_VENTANA}')\
                .replace("'", '"')\
            
            file_parsed = json.loads(
                raw_file, parse_int=int
            )
            self.__configs_replaced = file_parsed
    
    @property
    def configs(self) -> dict:
        """
        The function `configs` returns a dictionary containing the replaced configurations.
        :return: The method `configs` is returning the value of `self.__configs_replaced`, which is
        expected to be a dictionary.
        """
        return self.__configs_replaced
