import math
import random
from game.rules import SCREEN_WIDTH, SCREEN_HEIGHT
from game.rules import Player, Bullet, Boss


class OrbitBullet:
    def __init__(
        self,
        center_x,
        center_y,
        orbit_radius=40,
        angle=0,
        angular_speed=0.04,
        bullet_radius=4
    ):
        self.center_x = center_x
        self.center_y = center_y

        self.orbit_radius = orbit_radius
        self.angle = angle
        self.angular_speed = angular_speed
        self.radius = bullet_radius

        self.x = center_x + math.cos(angle) * orbit_radius
        self.y = center_y + math.sin(angle) * orbit_radius

    def update(self):
        self.angle += self.angular_speed

        self.x = (
            self.center_x
            + math.cos(self.angle) * self.orbit_radius
        )
        self.y = (
            self.center_y
            + math.sin(self.angle) * self.orbit_radius
        )


    

def create_orbit_circle(
    center_x,
    center_y,
    bullets,
    count=12,
    orbit_radius=40,
    angular_speed=0.04
):
    for i in range(count):
        angle = 2 * math.pi * i / count

        bullet = OrbitBullet(
            center_x,
            center_y,
            orbit_radius,
            angle,
            angular_speed
        )

        bullets.append(bullet)
