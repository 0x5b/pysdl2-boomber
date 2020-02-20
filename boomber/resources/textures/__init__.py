"""Provide tools for color textures."""

import sdl2.ext


step = 65

TEXTURE_SIZE = (step, step)
RESOURCES = sdl2.ext.Resources(__file__)

color_map = {
    "black": sdl2.ext.Color(0, 0, 0),
    "blue": sdl2.ext.Color(0, 0, 255),
    "darkred": sdl2.ext.Color(139, 0, 0),
    "grey": sdl2.ext.Color(105, 105, 105),
    "red": sdl2.ext.Color(255, 0, 0),
    "silver": sdl2.ext.Color(192, 192, 192),
    "white": sdl2.ext.Color(255, 255, 255),
    "yellow": sdl2.ext.Color(255, 255, 0),
}

direction_map = {
    "right": "right.png",
    "up": "up.png",
    "down": "down.png",
}


class TextureSpriteFactory(object):
    factory = None

    def __init__(self, renderer):
        self.factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=renderer)

    def get_color_texture(self, color):
        return self.factory.from_color(color_map[color], size=TEXTURE_SIZE)

    def get_texture(self, name):
        return self.factory.from_image(RESOURCES.get_path(name))
