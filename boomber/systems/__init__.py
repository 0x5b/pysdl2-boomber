"""Provides all systems of the game."""

import random
import time

import sdl2
import sdl2.ext

from boomber import Game
from boomber.components import (
    AIData,
    AnimationData,
    CollisionData,
    ControlData,
    DestroyData,
    PlayerData,
    SpriteAnimationData,
    Timer,
    Velocity,
)
from boomber.entities import Enemy
from boomber.sprites import MutableTextureSprite, step, tile_size


game = Game()


class TextureRenderer(sdl2.ext.TextureSpriteRenderSystem):
    """Common renderer system, that supports spritesheet animation."""

    def __init__(self, window):
        super().__init__(window)
        self.componenttypes = (MutableTextureSprite,)

    def render(self, sprites):
        self._renderer.clear()
        rcopy = sdl2.render.SDL_RenderCopyEx
        renderer = self.sdlrenderer
        for sprite in sprites:
            if sprite.frame is not None:
                sdl2.render.SDL_SetTextureBlendMode(sprite.texture,
                                                    sdl2.blendmode.SDL_BLENDMODE_ADD)
                rcopy(renderer, sprite.texture,
                      sdl2.rect.SDL_Rect(sprite.frame * tile_size, 0,
                                         tile_size, tile_size),
                      sdl2.rect.SDL_Rect(sprite.x, sprite.y,
                                         tile_size, tile_size),
                      sprite.angle, sprite.center, sprite.flip)
            else:
                r = sdl2.rect.SDL_Rect(0, 0, 0, 0)
                r.x = sprite.x
                r.y = sprite.y
                r.w, r.h = sprite.size
                rcopy(renderer, sprite.texture,
                      None, r, sprite.angle,
                      sprite.center, sprite.flip)
        sdl2.render.SDL_RenderPresent(self.sdlrenderer)


class MovementSystem(sdl2.ext.Applicator):
    def __init__(self):
        super().__init__()
        self.componenttypes = (Velocity, CollisionData,
                               PlayerData, sdl2.ext.Sprite,)

    def process(self, world, componentsets):
        for velocity, collisiondata, playerdata, sprite in componentsets:
            collisiondata.x = sprite.x
            collisiondata.y = sprite.y

            sprite.x += velocity.vx
            sprite.y += velocity.vy

            velocity.vx = 0
            velocity.vy = 0


class CollisionSystem(sdl2.ext.Applicator):
    def __init__(self):
        super().__init__()
        self.componenttypes = CollisionData, DestroyData, sdl2.ext.Sprite

    def _overlap(self, sprite, items):
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

            collision, _ = self._overlap(sprite, [game.player])
            if collision:
                if isinstance(destroydata.entity, Enemy):
                    game.player.destroydata.is_alive = False
                game.player.sprite.x = game.player.collisiondata.x
                game.player.sprite.y = game.player.collisiondata.y

            collision, _ = self._overlap(sprite, game.explosion_area)
            if collision:
                destroydata.is_alive = False

            collision, enemy = self._overlap(sprite, game.enemies)
            if collision:
                if isinstance(destroydata.entity, Enemy):
                    continue
                enemy.aidata.choose_direction = True
                enemy.aidata.collide_with = (sprite.x, sprite.y)


class TimerCallbackSystem(sdl2.ext.Applicator):
    def __init__(self):
        super().__init__()
        self.componenttypes = Timer, DestroyData, sdl2.ext.Sprite

    def process(self, world, componentsets):
        for timer, destroydata, sprite in componentsets:
            if time.time() - timer.start > timer.delta:
                if timer.callback == "explode":
                    game.explode(sprite.x, sprite.y)
                    destroydata.is_alive = False


class DestroySystem(sdl2.ext.Applicator):
    def __init__(self):
        super().__init__()
        self.componenttypes = DestroyData, sdl2.ext.Sprite

    def process(self, world, componentsets):
        for destroydata, sprite in componentsets:
            if not destroydata.is_alive and destroydata.is_destroyable:
                game.entities_to_delete.append(destroydata.entity)


class ControlSystem(sdl2.ext.Applicator):
    def __init__(self):
        super().__init__()
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
                game.plant_bomb(sprite.x, sprite.y)
                controldata.event = None


class AnimationSystem(sdl2.ext.Applicator):
    def __init__(self):
        super().__init__()
        self.componenttypes = Velocity, sdl2.ext.Sprite, AnimationData

    def process(self, world, componentsets):
        for velocity, sprite, animdata in componentsets:
            if velocity.vx > 0:
                sprite.texture = animdata.right
            if velocity.vx < 0:
                sprite.texture = animdata.left
            if velocity.vy > 0:
                sprite.texture = animdata.down
            if velocity.vy < 0:
                sprite.texture = animdata.up


class SpriteAnimationSystem(sdl2.ext.Applicator):
    def __init__(self):
        super().__init__()
        self.componenttypes = sdl2.ext.Sprite, SpriteAnimationData, DestroyData

    def process(self, world, componentsets):
        for sprite, animdata, destroydata in componentsets:
            if animdata.previous_tick is None:
                animdata.previous_tick = sdl2.SDL_GetTicks()
                sprite.frame = animdata.current_frame
            elif animdata.current_frame == 11:
                destroydata.is_alive = False
                animdata.current_frame = 0
            else:
                ticks = sdl2.SDL_GetTicks()
                if (ticks - animdata.previous_tick) > animdata.delta:
                    animdata.current_frame += 1
                    animdata.previous_tick = ticks
                sprite.frame = animdata.current_frame


class AIController(sdl2.ext.Applicator):
    def __init__(self):
        super().__init__()
        self.componenttypes = Velocity, sdl2.ext.Sprite,\
            AIData, CollisionData

    def process(self, world, componentsets):
        for velocity, sprite, aidata, collisiondata in componentsets:

            if aidata.choose_direction:
                collide_x, collide_y = aidata.collide_with
                if velocity.vx > 0:
                    sprite.x = collide_x - step
                if velocity.vx < 0:
                    sprite.x = collide_x + step
                if velocity.vy > 0:
                    sprite.y = collide_y - step
                if velocity.vy < 0:
                    sprite.y = collide_y + step

                vx, vy = random.choice(aidata.available_directions)
                velocity.vx = vx
                velocity.vy = vy
                aidata.choose_direction = False

            sprite.x += velocity.vx
            sprite.y += velocity.vy
