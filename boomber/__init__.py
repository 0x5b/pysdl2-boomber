import os

import sdl2
import sdl2.ext

from boomber.entities import (
    Block,
    Bomb,
    Enemy,
    Explosion,
    Player,
    Tile,
)
from boomber.sprites import SpriteFactory, tile_size


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
        self.sfactory = SpriteFactory(self.systems.get("spriterenderer"))

        for system in self.systems.values():
            self.world.add_system(system)

    def plant_bomb(self, x, y):
        if len(self.bombs) < self.player.playerdata.max_bombs:
            sprite = self.sfactory.bomb()
            self.bombs.append(Bomb(self.world, sprite, x, y))

    def explode(self, center_x, center_y):
        for r in range(1, self.player.playerdata.max_range * 2 + 1):
            r = r / 2.0
            for x, y in ((-tile_size * r, 0), (0, -tile_size * r),
                         (tile_size * r, 0), (0, tile_size * r), (0, 0)):
                sprite = self.sfactory.explosion()
                e = Explosion(self.world, sprite,
                              center_x + round(x), center_y + round(y))
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
        velocity = [(3, 0), (0, 3), (3, 0), (0, 3), (3, 0), (0, 3)]
        start_position = 50

        path = os.path.join("boomber", "resources", "levels", str(level))
        if not os.path.exists(path):
            return False

        sprite = self.sfactory.background()
        Tile(self.world, sprite, start_position, start_position)

        with open(path) as f:
            y = start_position
            for line in f:
                x = start_position
                for ch in line:
                    if ch == "x":
                        sprite = self.sfactory.wall()
                        Block(self.world, sprite, x, y, False)
                    elif ch == "b":
                        sprite = self.sfactory.block()
                        Block(self.world, sprite, x, y, True)
                    elif ch == "p":
                        sprite = self.sfactory.player()
                        self.player = Player(self.world, sprite, x, y)
                    elif ch == "e":
                        vx, vy = velocity.pop(0)
                        sprite = self.sfactory.enemy()
                        enemy = Enemy(self.world, sprite, x, y)
                        enemy.velocity.vx, enemy.velocity.vy = vx, vy

                        right = self.sfactory.tfactory.get_texture("right.png")
                        left = self.sfactory.tfactory.get_texture("left.png")
                        down = self.sfactory.tfactory.get_texture("down.png")
                        up = self.sfactory.tfactory.get_texture("up.png")
                        enemy.animationdata.right = right
                        enemy.animationdata.left = left
                        enemy.animationdata.down = down
                        enemy.animationdata.up = up

                        self.enemies.append(enemy)
                    x += tile_size
                y += tile_size
        return True
