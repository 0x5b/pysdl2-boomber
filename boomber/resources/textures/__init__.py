"""Provide tools for color textures."""

import sdl2.ext


TEXTURE_SIZE = (40, 40)

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


class TextureSpriteFactory(object):
    factory = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(TextureSpriteFactory, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super(TextureSpriteFactory, self).__init__()
        self.factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

    def get_color_texture(self, color):
        return self.factory.from_color(color_map[color], size=TEXTURE_SIZE)
