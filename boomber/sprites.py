"""Provide tools for sprites."""

import sdl2.ext

from sdl2.ext.common import SDLError


RESOURCES = sdl2.ext.Resources(__file__, "resources", "textures")

tile_size = 65
"""Size that sprite expect from every frame of texture."""

step = tile_size
"""Size of step for Player."""


class MutableTextureSprite(sdl2.ext.Sprite):
    def __init__(self, texture):
        super().__init__()

        self.texture = texture
        self.angle = 0.0
        self.flip = sdl2.render.SDL_FLIP_NONE
        self._size = tile_size, tile_size
        self._center = None

    def __del__(self):
        """Releases the bound SDL_Texture."""

        if self.texture is not None:
            sdl2.render.SDL_DestroyTexture(self.texture)
        self.texture = None

    @property
    def size(self):
        return self._size

    @property
    def center(self):
        return self._center


class SpriteFactory:

    def __init__(self, renderer):
        self.tfactory = TextureFactory(renderer)

    def bomb(self):
        t = self.tfactory.get_texture("bomb.png")
        return MutableTextureSprite(t)

    def explosion(self):
        c = self.tfactory.get_color_texture("yellow")
        return MutableTextureSprite(c)

    def wall(self):
        t = self.tfactory.get_texture("wall.png")
        return MutableTextureSprite(t)

    def block(self):
        t = self.tfactory.get_texture("block.png")
        return MutableTextureSprite(t)

    def player(self):
        t = self.tfactory.get_texture("idle.png")
        return MutableTextureSprite(t)

    def enemy(self):
        t = self.tfactory.get_texture("right.png")
        return MutableTextureSprite(t)


class TextureFactory(sdl2.ext.SpriteFactory):

    def __init__(self, renderer):
        super().__init__(renderer=renderer)

    def get_texture(self, name):
        """Return SDL_Texture object by name."""

        path = RESOURCES.get_path(name)
        image = sdl2.ext.image.load_image(path)

        return self.from_surface(image)

    def from_surface(self, tsurface):
        """Create a Texture from the passed SDL_Surface."""

        renderer = self.default_args["renderer"]

        texture = sdl2.render.SDL_CreateTextureFromSurface(
            renderer.sdlrenderer, tsurface)
        if not texture:
            raise SDLError()

        sdl2.surface.SDL_FreeSurface(tsurface)
        return texture