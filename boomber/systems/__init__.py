"""Provides all systems of the game."""

import sys
import time

import sdl2.ext

from boomber.components import (
    CollisionData,
    ControlData,
    DestroyData,
    PlayerData,
    Timer,
    Velocity,
)
from boomber.entities import (
    Bomb,
    Enemy,
    Explosion,
    Player,
)
from boomber.resources.textures import TextureSpriteFactory, step


FACTORY = TextureSpriteFactory()


class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    def render(self, comps):
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super(SoftwareRenderer, self).render(comps)


class MovementSystem(sdl2.ext.Applicator):
    def __init__(self):
        super(MovementSystem, self).__init__()
        self.componenttypes = (Velocity, CollisionData,
                               PlayerData, sdl2.ext.Sprite,)

    def process(self, world, componentsets):
        for velocity, collisiondata, playerdata, sprite in componentsets:
            collisiondata.x_in_world = sprite.x
            collisiondata.y_in_world = sprite.y

            sprite.x += velocity.vx
            sprite.y += velocity.vy

            if not playerdata.ai:
                velocity.vx = 0
                velocity.vy = 0


class CollisionSystem(sdl2.ext.Applicator):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(CollisionSystem, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super(CollisionSystem, self).__init__()
        self.componenttypes = CollisionData, DestroyData, sdl2.ext.Sprite
        self.player = None
        self.enemies = None
        self.explosion_area = []

    def _overlap(self, pos, sprite, items):
        left, top, right, bottom = sprite.area
        collision = False
        subject = None

        for subject in items:
            pleft, ptop, pright, pbottom = subject.sprite.area

            if subject.sprite == sprite:
                return False, subject

            collision = (pleft < right and pright > left and
                         ptop < bottom and pbottom > top)
            if collision:
                break
        return collision, subject

    def process(self, world, componentsets):
        for pos, destroydata, sprite in componentsets:

            collision, _ = self._overlap(pos, sprite, [self.player])
            if collision:
                if isinstance(destroydata.entity, Enemy):
                    self.player.destroydata.is_alive = False
                self.player.sprite.x = self.player.collisiondata.x_in_world
                self.player.sprite.y = self.player.collisiondata.y_in_world

            collision, _ = self._overlap(pos, sprite, self.explosion_area)
            if collision:
                destroydata.is_alive = False

            collision, enemy = self._overlap(pos, sprite, self.enemies)
            if collision:
                enemy.velocity.vx = -enemy.velocity.vx
                enemy.velocity.vy = -enemy.velocity.vy


class TimerSystem(sdl2.ext.Applicator):
    def __init__(self):
        super(TimerSystem, self).__init__()
        self.collision_system = CollisionSystem()
        self.componenttypes = Timer, DestroyData, sdl2.ext.Sprite

    def process(self, world, componentsets):
        for timer, destroydata, sprite in componentsets:
            if time.time() - timer.start > timer.delta:
                if timer.callback == "delete":
                    destroydata.is_alive = False
                if timer.callback == "explode":
                    for x, y in ((-step, 0), (0, -step), (step, 0), (0, step), (0, 0)):
                        sp_explosion = FACTORY.get_color_texture("yellow")
                        e = Explosion(world, sp_explosion,
                                      sprite.x + x, sprite.y + y)
                        self.collision_system.explosion_area.append(e)
                    destroydata.is_alive = False


class DestroySystem(sdl2.ext.Applicator):
    def __init__(self):
        super(DestroySystem, self).__init__()
        self.collision_system = CollisionSystem()
        self.componenttypes = DestroyData, sdl2.ext.Sprite

    def process(self, world, componentsets):
        for destroydata, sprite in componentsets:
            if not destroydata.is_alive and destroydata.is_destroyable:

                if destroydata.entity in self.collision_system.explosion_area:
                    self.collision_system.explosion_area.remove(destroydata.entity)

                if destroydata.entity in self.collision_system.enemies:
                    self.collision_system.enemies.remove(destroydata.entity)
                    if not len(self.collision_system.enemies):
                        print("YOU WON!")
                        sys.exit(0)

                if isinstance(destroydata.entity, Player):
                    print("GAME OVER!")
                    sys.exit(0)

                world.delete(destroydata.entity)


class ControlSystem(sdl2.ext.Applicator):
    def __init__(self):
        super(ControlSystem, self).__init__()
        self.componenttypes = ControlData, Velocity, sdl2.ext.Sprite

    def process(self, world, componentsets):
        for controldata, velocity, sprite in componentsets:
            if not controldata.event:
                break
            if controldata.event == sdl2.SDLK_UP:
                velocity.vy = -step
                controldata.event = None
            elif controldata.event == sdl2.SDLK_DOWN:
                velocity.vy = step
                controldata.event = None
            elif controldata.event == sdl2.SDLK_LEFT:
                velocity.vx = -step
                controldata.event = None
            elif controldata.event == sdl2.SDLK_RIGHT:
                velocity.vx = step
                controldata.event = None
            elif controldata.event == sdl2.SDLK_SPACE:
                sp_bomb = FACTORY.get_color_texture("darkred")
                Bomb(world, sp_bomb, sprite.x, sprite.y)
                controldata.event = None
