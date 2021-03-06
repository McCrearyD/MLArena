from typing import List, Tuple
from actors.actor import *
import arcade
import numpy as np

LENGTH = 30
WIDTH = 5


class Laser(Actor):
    start_pos: Tuple[float]
    speed: float

    wrapped = False

    min_life_span: float
    max_life_span: float

    damage: float

    is_dead = False
    color: tuple

    traveled = 0

    firing_actor: Actor

    def __init__(
        self,
        actor: Actor,
        pos: List[float],
        direc: float,
        speed: float = 500,
        min_life_span: float = 0,
        max_life_span: float = 500,
        damage: float = 8,
        color: tuple = arcade.color.RED
    ):
        """
        Args:
            pos (List[float]): Starting position for the laser. (Should be the same as the firing actor.)
            direc (float): Fixed direction of the laser. (Should be the same as the firing actor.)
            speed (float): Speed of the laser.
            min_life_span (float): Minimum travel distance.
            max_life_span (float): Maximum travel distance.
        """

        self.firing_actor = actor
        self.speed = speed
        self.direc = direc
        self.pos = list(pos)
        self.start_pos = (pos[0], pos[1])
        self.min_life_span = min_life_span
        self.max_life_span = max_life_span
        self.damage = damage
        self.color = color

    def get_damage(self):
        """
        Returns the amount of damage the laser should deal at this point.

        Returns 0 if not within active range
        """

        if self.traveled < self.min_life_span:
            return 0

        return self.damage

    def get_head_position(self):
        """Returns the position of the head end of the laser."""
        return (self.pos[0] + math.cos(self.direc) * LENGTH, self.pos[1] + math.sin(self.direc) * LENGTH)

    def kill(self):
        self.is_dead = True

    def update(self, delta_time):
        if self.is_dead:
            return

        dx = math.cos(self.direc) * (self.speed * delta_time)
        dy = math.sin(self.direc) * (self.speed * delta_time)

        self.traveled += math.sqrt(dx ** 2 + dy ** 2)

        self.pos[0] += dx
        self.pos[1] += dy

        if self.wrapX():
            self.wrapped = True
        if self.wrapY():
            self.wrapped = True

        if self.traveled > self.max_life_span:
            self.kill()

    def draw(self, specific_color=None):
        if self.is_dead:
            return

        color = self.color

        # If it has a min life span, color it differently when less than.
        if self.traveled < self.min_life_span:
            color = arcade.color.RED_DEVIL

        if specific_color != None:
            color = specific_color

        hp = self.get_head_position()
        arcade.draw_line(self.pos[0], self.pos[1],
                         hp[0], hp[1], color, WIDTH)

    def get_dist_if_in_path(self, C, r):
        """
        This method takes in the center & radius of a circle, and determines weather it's in
        this lasers path, and if so returns the distance squared.

        Returns:
            -1 if not in path, otherwise distance squared from the circle radius point to the laser head.
        """

        E = self.get_head_position()
        L = [
            E[0] + math.cos(self.direc) * SCREEN_WIDTH,
            E[1] + math.sin(self.direc) * SCREEN_HEIGHT,
        ]

        d = np.subtract(L, E)
        f = np.subtract(E, C)

        a = np.dot(d, d)
        b = 2*np.dot(f, d)
        c = np.dot(f, f) - r*r

        discriminant = b*b-4*a*c

        if discriminant >= 0:
            # If this laser is on track to collide, return
            # distance squared.
            return (E[0]-C[0])**2 + (E[1]-C[0])**2

        return -1
