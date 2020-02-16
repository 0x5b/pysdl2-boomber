import os
import sys

import sdl2
import sdl2.ext

from boomber import entities
from boomber import systems

from boomber.resources.textures import TextureSpriteFactory


def create_map(world, level):

    factory = TextureSpriteFactory()
    enemies = []
    start_position = 50
    step = 40

    with open(os.path.join("boomber", "resources", "levels", str(level))) as f:
        y = start_position
        for line in f:
            x = start_position
            for ch in line:
                if ch == "x":
                    sp_block = factory.get_color_texture("grey")
                    entities.Block(world, sp_block, x, y, False)
                if ch == "b":
                    sp_block = factory.get_color_texture("silver")
                    entities.Block(world, sp_block, x, y, True)
                if ch == "p":
                    sp_player = factory.get_color_texture("blue")
                    player = entities.Player(world, sp_player, x, y)
                if ch == "e":
                    sp_enemy = factory.get_color_texture("red")
                    enemy = entities.Enemy(world, sp_enemy, x, y)
                    enemies.append(enemy)
                x += step
            y += step

    return player, enemies


def run():
    sdl2.ext.init()

    window = sdl2.ext.Window("Boomber", size=(860, 600))
    world = sdl2.ext.World()

    timer_system = systems.TimerSystem()
    destroy_system = systems.DestroySystem()
    movement_system = systems.MovementSystem()
    collision_system = systems.CollisionSystem()
    control_system = systems.ControlSystem()
    spriterenderer = systems.SoftwareRenderer(window)

    world.add_system(timer_system)
    world.add_system(destroy_system)
    world.add_system(movement_system)
    world.add_system(collision_system)
    world.add_system(control_system)
    world.add_system(spriterenderer)

    player, enemies = create_map(world, 1)
    collision_system.player = player
    collision_system.enemies = enemies

    window.show()

    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym in (sdl2.SDLK_UP, sdl2.SDLK_DOWN,
                                            sdl2.SDLK_LEFT, sdl2.SDLK_RIGHT,
                                            sdl2.SDLK_SPACE):
                    player.controldata.event = event.key.keysym.sym
        sdl2.SDL_Delay(10)
        world.process()
    return 0


if __name__ == "__main__":
    sys.exit(run())
