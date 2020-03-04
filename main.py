import sys

import sdl2
import sdl2.ext

from boomber import Game
from boomber import systems


def run():
    sdl2.ext.init()

    window = sdl2.ext.Window("Boomber", size=(1335, 900))

    game_systems = {}
    game_systems["timer_system"] = systems.TimerCallbackSystem()
    game_systems["destroy_system"] = systems.DestroySystem()
    game_systems["movement_system"] = systems.MovementSystem()
    game_systems["collision_system"] = systems.CollisionSystem()
    game_systems["control_system"] = systems.ControlSystem()
    game_systems["animation_system"] = systems.AnimationSystem()
    game_systems["ai_system"] = systems.AIController()
    game_systems["spriterenderer"] = systems.TextureRenderer(window)

    game = Game(window=window, systems=game_systems)
    game.start()


if __name__ == "__main__":
    sys.exit(run())
