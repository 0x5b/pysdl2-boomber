import os

import sdl2
import sdl2.ext

from boomber.entities import (
    Block,
    Bomb,
    Enemy,
    Explosion,
    Player,
)
from boomber.resources.textures import TextureSpriteFactory, step


class Game:
    """Main class, contains information about all systems and states."""

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, window=None, systems=None):
        sdl2.ext.init()

        self.player = None
        self.level = 1
        self.enemies = []
        self.bombs = []
        self.explosion_area = []
        self.entities_to_delete = []

        self.window = window or sdl2.ext.Window("OK, Boomber",
                                                size=(1335, 900))
        self.world = sdl2.ext.World()
        self.systems = systems or {}
        self.sprite_factory = TextureSpriteFactory(
            self.systems.get("spriterenderer"))

        for system in self.systems.values():
            self.world.add_system(system)

    def plant_bomb(self, x, y):
        if len(self.bombs) < self.player.playerdata.max_bombs:
            sp_bomb = self.sprite_factory.get_texture("bomb.png")
            self.bombs.append(Bomb(self.world, sp_bomb, x, y))

    def explode(self, center_x, center_y):
        for r in range(1, self.player.playerdata.max_range + 1):
            for x, y in ((-step * r, 0), (0, -step * r),
                         (step * r, 0), (0, step * r), (0, 0)):
                sp_explosion = self.sprite_factory.get_color_texture("yellow")
                e = Explosion(self.world, sp_explosion,
                              center_x + x, center_y + y)
                self.explosion_area.append(e)

    def process(self):
        for e in self.entities_to_delete:
            if e in self.explosion_area:
                self.explosion_area.remove(e)
            if e is self.player:
                self.stop("game over!")
            if e in self.enemies:
                self.enemies.remove(e)
                if not self.enemies:
                    self.stop("you won!")
            if e in self.bombs:
                self.bombs.remove(e)
            self.world.delete(e)

    def stop(self, message=None):
        if message:
            print(message)
        self.running = False

    def start(self):
        self.create_map(self.level)
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
            self.world.process()
            self.process()

            sdl2.SDL_Delay(10)
        return 0

    def create_map(self, level):

        velocity = [(-3, 0), (0, 4), (-4, 0), (0, 4), (-5, 0), (0, 4)]
        start_position = 50
        step = 65

        path = os.path.join("boomber", "resources", "levels", str(level))
        if not os.path.exists(path):
            return False

        with open(path) as f:
            y = start_position
            for line in f:
                x = start_position
                for ch in line:
                    if ch == "x":
                        Block(self.world,
                              self.sprite_factory.get_texture("wall.png"),
                              x, y, False)
                    if ch == "b":
                        Block(self.world,
                              self.sprite_factory.get_texture("block.png"),
                              x, y, True)
                    if ch == "p":
                        self.player = Player(
                            self.world,
                            self.sprite_factory.get_color_texture("blue"), x, y)
                    if ch == "e":
                        vx, vy = velocity.pop(0)
                        if vy == 0:
                            sp_enemy = self.sprite_factory.get_texture("right.png")
                        else:
                            sp_enemy = self.sprite_factory.get_texture("down.png")
                        enemy = Enemy(self.world, sp_enemy, x, y)
                        enemy.velocity.vx, enemy.velocity.vy = vx, vy
                        self.enemies.append(enemy)
                    x += step
                y += step
        return True
