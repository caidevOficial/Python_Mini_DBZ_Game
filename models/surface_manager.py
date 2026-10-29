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

import os
import pygame as pg

class SurfaceManager:
    # Nivel 1: Imágenes maestras cargadas desde disco (evita lecturas duplicadas de disco)
    _master_cache: dict[str, pg.Surface] = {}

    # Nivel 2: Listas de frames de spritesheets recortados y transformados
    _spritesheet_cache: dict[tuple, list[pg.Surface]] = {}

    # Nivel 3: Superficies individuales escaladas (fondos, plataformas)
    _surface_cache: dict[tuple, pg.Surface] = {}

    @classmethod
    def _normalize_path(cls, path: str) -> str:
        return os.path.normpath(path).replace("\\", "/")

    @classmethod
    def _get_master_surface(cls, norm_path: str, convert_alpha: bool = True) -> pg.Surface:
        """Carga y convierte la superficie maestra asegurando una única lectura física de disco."""
        if norm_path not in cls._master_cache:
            if not os.path.exists(norm_path):
                raise FileNotFoundError(f"No se encontró el recurso gráfico: {norm_path}")

            raw_img = pg.image.load(norm_path)
            # Si el subsistema de video ya está inicializado, convertir formato de píxeles
            if pg.display.get_surface() is not None:
                cls._master_cache[norm_path] = raw_img.convert_alpha() if convert_alpha else raw_img.convert()
            else:
                cls._master_cache[norm_path] = raw_img

        return cls._master_cache[norm_path]

    @staticmethod
    def get_surface_from_spritesheet(
        img_path: str,
        cols: int,
        rows: int,
        step: int = 1,
        scale_2x: bool = True,
        dimentions: tuple = None,
        flip: bool = False,
        dimensions: tuple = None
    ) -> list[pg.surface.Surface]:
        """
        Divide un spritesheet en una lista de superficies con soporte de caché multinivel.
        Soporta los parámetros 'dimentions' (compatibilidad heredada) y 'dimensions'.
        """
        norm_path = SurfaceManager._normalize_path(img_path)
        target_dimensions = dimensions if dimensions is not None else dimentions
        dim_key = tuple(target_dimensions) if target_dimensions is not None else None

        # Clave compuesta única inmutable para la caché
        cache_key = (
            norm_path,
            int(cols),
            int(rows),
            int(step),
            bool(scale_2x),
            dim_key,
            bool(flip)
        )

        # Retorno inmediato de la caché de Nivel 2 si ya fue procesado
        if cache_key in SurfaceManager._spritesheet_cache:
            return list(SurfaceManager._spritesheet_cache[cache_key])

        # Obtiene la imagen maestra (se carga de disco solo si es la primera vez)
        surface_img = SurfaceManager._get_master_surface(norm_path, convert_alpha=True)

        frame_width = int(surface_img.get_width() / cols)
        frame_height = int(surface_img.get_height() / rows)
        sprites_list: list[pg.surface.Surface] = []

        for row in range(rows):
            for column in range(0, cols, step):
                x_axis = column * frame_width
                y_axis = row * frame_height

                frame_surface = surface_img.subsurface(
                    x_axis, y_axis, frame_width, frame_height
                )

                if flip:
                    frame_surface = pg.transform.flip(frame_surface, True, False)
                if scale_2x:
                    frame_surface = pg.transform.scale2x(frame_surface)
                if target_dimensions:
                    frame_surface = pg.transform.scale(frame_surface, target_dimensions)

                sprites_list.append(frame_surface)

        # Almacenar en caché procesada
        SurfaceManager._spritesheet_cache[cache_key] = sprites_list
        return list(sprites_list)

    @staticmethod
    def get_surface(img_path: str, dimensions: tuple = None, convert_alpha: bool = True) -> pg.surface.Surface:
        """
        Carga y almacena en caché una superficie individual (fondos de pantalla, plataformas).
        Aplica .convert() o .convert_alpha() y escalado optimizado.
        """
        norm_path = SurfaceManager._normalize_path(img_path)
        dim_key = tuple(dimensions) if dimensions is not None else None
        cache_key = (norm_path, dim_key, bool(convert_alpha))

        if cache_key in SurfaceManager._surface_cache:
            return SurfaceManager._surface_cache[cache_key]

        master = SurfaceManager._get_master_surface(norm_path, convert_alpha=convert_alpha)

        if dim_key:
            scaled_surface = pg.transform.scale(master, dim_key)
        else:
            scaled_surface = master

        SurfaceManager._surface_cache[cache_key] = scaled_surface
        return scaled_surface

    @classmethod
    def clear_cache(cls) -> None:
        """Libera la memoria de la caché si es necesario."""
        cls._master_cache.clear()
        cls._spritesheet_cache.clear()
        cls._surface_cache.clear()

    @classmethod
    def get_cache_stats(cls) -> dict:
        """Información de diagnóstico sobre recursos en memoria."""
        return {
            "master_images_loaded": len(cls._master_cache),
            "processed_spritesheet_variations": len(cls._spritesheet_cache),
            "single_surfaces_cached": len(cls._surface_cache)
        }
