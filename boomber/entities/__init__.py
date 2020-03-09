"""Provides all entities of the game."""

import sdl2.ext

from boomber import components


class Tile(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx, posy):
        self.sprite = sprite
        self.sprite.position = posx, posy


class Moveable(Tile):
    def __init__(self, world, sprite, posx, posy):
        super(Moveable, self).__init__(world, sprite, posx, posy)

        self.velocity = components.Velocity()
        self.destroydata = components.DestroyData()
        self.destroydata.entity = self
        self.collisiondata = components.CollisionData(posx, posy)


class Player(Moveable):
    def __init__(self, world, sprite, posx, posy):
        super(Player, self).__init__(world, sprite, posx, posy)

        self.playerdata = components.PlayerData()
        self.controldata = components.ControlData()


class Enemy(Moveable):
    def __init__(self, world, sprite, posx, posy):
        super(Enemy, self).__init__(world, sprite, posx, posy)

        self.aidata = components.AIData()
        self.animationdata = components.AnimationData()


class Block(Tile):
    def __init__(self, world, sprite, posx, posy, is_destroyable):
        super(Block, self).__init__(world, sprite, posx, posy)

        self.collisiondata = components.CollisionData(posx, posy)
        self.destroydata = components.DestroyData(is_destroyable)
        self.destroydata.entity = self


class Bomb(Tile):
    def __init__(self, world, sprite, posx, posy):
        super(Bomb, self).__init__(world, sprite, posx, posy)

        self.collisiondata = components.CollisionData(posx, posy)
        self.timer = components.Timer(2)
        self.timer.callback = "explode"
        self.destroydata = components.DestroyData()
        self.destroydata.entity = self


class Explosion(Tile):
    def __init__(self, world, sprite, posx, posy):
        super(Explosion, self).__init__(world, sprite, posx, posy)

        self.spriteanimationdata = components.SpriteAnimationData()
        self.destroydata = components.DestroyData()
        self.destroydata.entity = self
