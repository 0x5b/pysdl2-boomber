"""Provides all components of the game."""

import time


class Velocity(object):
    def __init__(self):
        self.vx = 0
        self.vy = 0


class CollisionData(object):
    def __init__(self, x, y):
        self.x_in_world = x
        self.y_in_world = y


class Timer(object):
    def __init__(self, delta):
        self.start = time.time()
        self.delta = delta
        self.callback = None


class DestroyData(object):
    def __init__(self, is_destroyable=True):
        self.is_alive = True
        self.is_destroyable = is_destroyable
        self.entity = None


class PlayerData(object):
    def __init__(self, ai=True):
        self.ai = ai
        self.max_bombs = 5
        self.max_range = 2


class ControlData(object):
    def __init__(self):
        self.event = None
