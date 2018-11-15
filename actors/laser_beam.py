import math
import arcade
import numpy as np

SPEED = 25
LENGTH = 20
WIDTH = 5
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600


class LaserBeam:
    def __init__(self, pos, direction, life_span, damage, speed, color):
        """
        Laser beam data structure.
        @param pos Starting position.
        @param direction Constant heading direction.
        @param life_span How far the laser will travel until it's deletion.
        @param damage How much damage will be caused by this laser.
        @param speed How fast this laser will travel.
        """

        self.dir = direction
        self.start_pos = [pos[0], pos[1]]
        self.pos = pos
        self.damage = damage
        self.speed = speed
        self.color = color

        self.life_span_squared = math.pow(life_span, 2)
        self.killed = None
        self.end_of_life = False

    def get_damage(self):
        """
        @return Returns the amount of damage to be inflicted by this laser.
        """

        return self.damage

    def kill(self, pawn):
        """
        Alters the killed & end_of_life field variables ensuring that the given pawn
        will be killed, and the calling laser will be deleted.
        """

        self.killed = pawn
        self.end_of_life = True

    def who_was_killed(self):
        """
        Denotes which pawn the laser collided with.
        @return Returns the killed field variable.
        """

        return self.killed

    def update(self, delta_time):
        """
        Handles updating the laser's position & if it's out of range it will be delted.
        @return Returns False if this laser should be deleted. (aka went off screen, landed a shot, or went out of range).
        """

        if self.killed != None or self.end_of_life:
            return False

        self.pos[0] += math.cos(self.dir) * self.speed * delta_time
        self.pos[1] += math.sin(self.dir) * self.speed * delta_time

        dist_squared = math.pow(
            self.start_pos[0]-self.pos[0], 2) + math.pow(self.start_pos[1]-self.pos[1], 2)

        if dist_squared > self.life_span_squared:
            return False

        if self.pos[0] > SCREEN_WIDTH or self.pos[0] < 0:
            return False

        if self.pos[1] > SCREEN_HEIGHT or self.pos[1] < 0:
            return False

    def draw(self):
        """
        Draws the laser body from it's tail to head.
        """

        hp = self.get_head_position()

        arcade.draw_line(self.pos[0], self.pos[1],
                         hp[0], hp[1], self.color, WIDTH)

    def get_dir(self):
        """
        @return Returns this laser's heading direction in radians.
        """

        return self.dir

    def get_speed(self):
        """
        @return Returns this laser's speed.
        """

        return self.speed

    def is_in_path(self, C, r):
        """
        This method checks to see if the given center with radius is in the path of
        this laser.
        """

        E = [self.pos[0], self.pos[1]]
        L = [
            E[0] + math.cos(self.dir) * SCREEN_WIDTH,
            E[1] + math.sin(self.dir) * SCREEN_HEIGHT,
        ]

        d = np.subtract(L, E)
        f = np.subtract(E, C)

        a = np.dot(d, d)
        b = 2*np.dot(f, d)
        c = np.dot(f, f) - r*r

        discriminant = b*b-4*a*c

        return discriminant >= 0

    def get_vec(self):
        """
        Returns the vector of dir
        """

        return (math.cos(self.dir), math.sin(self.dir))

    def get_head_position(self):
        """
        Returns the position of the head end of the laser.
        """

        return (self.pos[0] + math.cos(self.dir) * LENGTH, self.pos[1] + math.sin(self.dir) * LENGTH)
