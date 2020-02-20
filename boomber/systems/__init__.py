"""Provides all systems of the game."""

import sys
import time

import sdl2
import sdl2.ext

from boomber import Game
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
from boomber.resources.textures import step


game = Game()


class TextureRenderer(sdl2.ext.TextureSpriteRenderSystem):
    def __init__(self, window):
        super(TextureRenderer, self).__init__(window)

    def render(self, comps):
        self._renderer.clear()
        super(TextureRenderer, self).render(comps)


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

    def __init__(self):
        super(CollisionSystem, self).__init__()
        self.componenttypes = CollisionData, DestroyData, sdl2.ext.Sprite
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

            collision, _ = self._overlap(pos, sprite, [game.player])
            if collision:
                if isinstance(destroydata.entity, Enemy):
                    game.player.destroydata.is_alive = False
                game.player.sprite.x = game.player.collisiondata.x_in_world
                game.player.sprite.y = game.player.collisiondata.y_in_world

            collision, _ = self._overlap(pos, sprite, self.explosion_area)
            if collision:
                destroydata.is_alive = False

            collision, enemy = self._overlap(pos, sprite, game.enemies)
            if collision:
                enemy.velocity.vx = -enemy.velocity.vx
                enemy.velocity.vy = -enemy.velocity.vy
                enemy.sprite.flip = 0 if enemy.sprite.flip else 1


class TimerSystem(sdl2.ext.Applicator):
    def __init__(self):
        super(TimerSystem, self).__init__()
        self.componenttypes = Timer, DestroyData, sdl2.ext.Sprite

    def process(self, world, componentsets):
        for timer, destroydata, sprite in componentsets:
            if time.time() - timer.start > timer.delta:
                if timer.callback == "delete":
                    destroydata.is_alive = False
                if timer.callback == "explode":
                    for x, y in ((-step, 0), (0, -step), (step, 0), (0, step), (0, 0)):
                        sp_explosion = game.sprite_factory.get_color_texture("yellow")
                        e = Explosion(world, sp_explosion,
                                      sprite.x + x, sprite.y + y)
                        game.collision_system.explosion_area.append(e)
                    destroydata.is_alive = False


class DestroySystem(sdl2.ext.Applicator):
    def __init__(self):
        super(DestroySystem, self).__init__()
        self.componenttypes = DestroyData, sdl2.ext.Sprite

    def process(self, world, componentsets):
        for destroydata, sprite in componentsets:
            if not destroydata.is_alive and destroydata.is_destroyable:

                if destroydata.entity in game.collision_system.explosion_area:
                    game.collision_system.explosion_area.remove(destroydata.entity)

                if destroydata.entity in game.enemies:
                    game.enemies.remove(destroydata.entity)
                    if not game.enemies:
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
                sp_bomb = game.sprite_factory.get_texture("bomb.png")
                Bomb(world, sp_bomb, sprite.x, sprite.y)
                controldata.event = None
