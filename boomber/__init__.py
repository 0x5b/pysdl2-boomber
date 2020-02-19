import os

import sdl2
import sdl2.ext

from boomber.entities import Player, Enemy, Block
from boomber.resources.textures import TextureSpriteFactory


class Game:
    """Main class, contains information about all systems and states."""

    _running = False
    _player = None
    enemies = []

    current_level = 1

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, window=None, systems=None):
        sdl2.ext.init()

        self._window = window or sdl2.ext.Window("OK, Boomber", size=(1335, 900))
        self._world = sdl2.ext.World()
        self._systems = systems or {}
        self._sprite_factory = TextureSpriteFactory()

        for system in self._systems.values():
            self.world.add_system(system)

    def start(self):

        self.create_map()
        self.window.show()

        self.running = True
        while self.running:
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    self.running = False
                if event.type == sdl2.SDL_KEYDOWN:
                    if event.key.keysym.sym in (sdl2.SDLK_UP, sdl2.SDLK_DOWN,
                                                sdl2.SDLK_LEFT, sdl2.SDLK_RIGHT,
                                                sdl2.SDLK_SPACE):
                        self.player.controldata.event = event.key.keysym.sym
            sdl2.SDL_Delay(10)
            self.world.process()
        return 0

    def create_map(self):

        velocity = [(4, 0), (0, 5), (4, 0), (0, 5), (5, 0), (0, 5)]
        start_position = 50
        step = 65

        path = os.path.join("boomber", "resources", "levels", str(self.level))
        with open(path) as f:
            y = start_position
            for line in f:
                x = start_position
                for ch in line:
                    if ch == "x":
                        Block(self.world,
                              self.sprite_factory.get_color_texture("grey"),
                              x, y, False)
                    if ch == "b":
                        Block(self.world,
                              self.sprite_factory.get_color_texture("silver"),
                              x, y, True)
                    if ch == "p":
                        self.player = Player(
                            self.world,
                            self.sprite_factory.get_color_texture("blue"), x, y)
                    if ch == "e":
                        vx, vy = velocity.pop(0)
                        if vy == 0:
                            sp_enemy = self.sprite_factory.get_texture("right")
                        else:
                            sp_enemy = self.sprite_factory.get_texture("down")
                        enemy = Enemy(self.world, sp_enemy, x, y)
                        enemy.velocity.vx, enemy.velocity.vy = vx, vy
                        self.enemies.append(enemy)
                    x += step
                y += step

    @property
    def world(self):
        return self._world

    @property
    def window(self):
        return self._window

    @property
    def sprite_factory(self):
        return self._sprite_factory

    @property
    def collision_system(self):
        return self._systems["collision_system"]

    @property
    def level(self):
        return self.current_level

    @level.setter
    def level(self, value):
        self.current_level = value

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, value):
        self._player = value

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, value):
        self._running = value
