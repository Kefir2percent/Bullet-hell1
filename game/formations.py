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
        bullet_radius=4,
        outward_speed=0.75,
        color = (255,255,255)
        
    ):
        self.center_x = center_x
        self.center_y = center_y

        self.orbit_radius = orbit_radius
        self.angle = angle
        self.angular_speed = angular_speed
        self.outward_speed = outward_speed
        self.radius = bullet_radius

        self.x = center_x + math.cos(angle) * orbit_radius
        self.y = center_y + math.sin(angle) * orbit_radius

        self.color = color

    def update(self):
        self.angle += self.angular_speed
        self.orbit_radius += self.outward_speed

        self.x = (
            self.center_x
            + math.cos(self.angle) * self.orbit_radius
        )
        self.y = (
            self.center_y
            + math.sin(self.angle) * self.orbit_radius
        )

    def is_off_screen(self):
        return (
            self.x < -self.radius
            or self.x > SCREEN_WIDTH + self.radius
            or self.y < -self.radius
            or self.y > SCREEN_HEIGHT + self.radius
        )



    

def create_orbit_circle(
    center_x,
    center_y,
    bullets,
    count=16,
    orbit_radius=15,
    angular_speed=0.008,
    bullet_radius=15,
):
    for i in range(count):
        angle = 2 * math.pi * i / count

        bullet = OrbitBullet(
            center_x,
            center_y,
            orbit_radius,
            angle,
            angular_speed,
            bullet_radius,
        )

        bullets.append(bullet)

def fire_at_player(boss, player, bullets, speed=2.0):
    dx = player.x - boss.x
    dy = player.y - boss.y

    distance = math.hypot(dx, dy)

    if distance == 0:
        return

    dx /= distance
    dy /= distance

    bullets.append(
    Bullet(
        boss.x, boss.y,
        dx, dy,
        speed=speed,
        radius=8
    )
    )


RAINBOW_COLORS = [
    (255, 60, 60),    # Red
    (255, 150, 40),   # Orange
    (255, 230, 60),   # Yellow
    (60, 220, 100),   # Green
    (60, 170, 255),   # Blue
    (170, 90, 255),   # Violet
]


class WinderBullet:
    def __init__(
        self,
        angle,
        direction=1,
        radial_speed=1.5,
        angular_speed=0.015,
        radius=6,
        color=(255, 255, 255)
    ):
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2

        self.distance = 600
        self.angle = angle

        self.radial_speed = radial_speed
        self.angular_speed = angular_speed * direction

        self.radius = radius
        self.color = color
        self.shape = "diamond"

        self.update_position()

    def update_position(self):
        self.x = (
            self.center_x
            + math.cos(self.angle) * self.distance
        )
        self.y = (
            self.center_y
            + math.sin(self.angle) * self.distance
        )

    def update(self):
        self.angle += self.angular_speed
        self.distance -= self.radial_speed
        self.update_position()

    def is_off_screen(self):
        return self.distance <= 0



def create_winder_wave(
    bullets,
    count=12,
    direction=1,
    angle_offset=0,
    radial_speed=1.5,
    angular_speed=0.015
):
    for i in range(count):
        angle = (
            2 * math.pi * i / count
            + angle_offset
        )

        color = RAINBOW_COLORS[i % len(RAINBOW_COLORS)]

        bullet = WinderBullet(
            angle=angle,
            direction=direction,
            radial_speed=radial_speed,
            angular_speed=angular_speed,
            color=color
        )

        bullets.append(bullet)

