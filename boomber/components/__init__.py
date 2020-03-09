"""Provides all components of the game."""

import time


class Velocity:
    def __init__(self):
        self.vx = 0
        self.vy = 0


class CollisionData:
    def __init__(self, x, y):
        self.x_in_world = x
        self.y_in_world = y


class Timer:
    def __init__(self, delta):
        self.start = time.time()
        self.delta = delta
        self.callback = None


class DestroyData:
    def __init__(self, is_destroyable=True):
        self.is_alive = True
        self.is_destroyable = is_destroyable
        self.entity = None


class PlayerData:
    def __init__(self):
        self.max_bombs = 1
        self.max_range = 1


class AIData:
    def __init__(self):
        self.available_directions = [(3, 0), (0, 3), (-3, 0), (0, -3)]
        self.choose_direction = False
        self.collide_with = None


class ControlData:
    def __init__(self):
        self.event = None


class AnimationData:
    def __init__(self):
        self.right = None
        self.down = None
        self.left = None
        self.up = None


class SpriteAnimationData:
    def __init__(self):
        self.current_frame = 0
        self.previous_tick = None
        self.delta = 25
