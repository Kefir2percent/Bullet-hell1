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

def fire_at_player(boss, player, bullets, speed):
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
    (255, 100, 120),  # Pink-red
    (255, 220, 150),  # Yellow
    (100, 255, 140),  # Green
    (100, 220, 255),  # Cyan
    (180, 150, 255),  # Purple
    (255, 245, 220),  # White
]


class WinderBullet:
    def __init__(
        self,
        angle,
        distance,
        angular_speed=0.012,
        radial_speed=2.0,
        color=(255, 255, 255),
        radius = 10
    ):
        # The center of the formation.
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2

        self.angle = angle
        self.distance = distance

        self.radius = radius

        self.angular_speed = angular_speed
        self.radial_speed = radial_speed

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
        # Rotate the trajectory while moving through the center.
        self.angle += self.angular_speed

        # Distance is signed: bullets can pass through zero
        # and emerge on the opposite side of the center.
        self.distance -= self.radial_speed

        self.update_position()

    def is_off_screen(self):
        return (
            self.x < -self.radius
            or self.x > SCREEN_WIDTH + self.radius
            or self.y < -self.radius
            or self.y > SCREEN_HEIGHT + self.radius
        )


def create_winder_wave(
    bullets,
    count=24,
    direction=1,
    angle_offset=0,
    radial_speed=2.0,
    angular_speed=0.012,
    radius = 10
):
    # Spawn bullets around a large ring.
    # Each wave is slightly rotated from the previous wave.
    spawn_distance = max(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.45

    for i in range(count):

        angle = (
            2 * math.pi * i / count
            + angle_offset
        )

        color = RAINBOW_COLORS[
            i % len(RAINBOW_COLORS)
        ]

        bullet = WinderBullet(
            angle=angle,
            distance=spawn_distance,
            angular_speed=angular_speed * direction,
            radial_speed=radial_speed,
            radius=10,
            color=color,
        )

        bullets.append(bullet)


class WallBullet:
    def __init__(self, x, y, dx, dy, speed=3.0, radius=7):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.radius = radius
        self.color = (100, 220, 255)
        self.shape = "circle"

    def update(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

    def is_off_screen(self):
        return (
            self.x < -self.radius
            or self.x > SCREEN_WIDTH + self.radius
            or self.y < -self.radius
            or self.y > SCREEN_HEIGHT + self.radius
        )


def create_wall_bullet(bullets, x, y, dx, dy, speed=3.0):
    bullets.append(
        WallBullet(x, y, dx, dy, speed=speed)
    )


def create_triangle_walls(
    bullets,
    top_x,
    top_y,
    left_x,
    right_x,
    bottom_y,
    spacing=25,
    speed=3.0,
):
    for bottom_x in (left_x, right_x):
        distance = math.hypot(
            bottom_x - top_x,
            bottom_y - top_y
        )
        steps = max(1, int(distance / spacing))

        dx = (bottom_x - top_x) / distance
        dy = (bottom_y - top_y) / distance

        for i in range(steps):
            t = i / steps

            x = top_x + (bottom_x - top_x) * t
            y = top_y + (bottom_y - top_y) * t

            create_wall_bullet(
                bullets,
                x, y,
                dx, dy,
                speed=speed
            )


def create_geometry_pattern(bullets, center_x, center_y, elapsed,
                            vertex_count=4, base_radius=180, speed=4.0):
    for i in range(vertex_count):
        angle = (2 * math.pi * i / vertex_count) + elapsed * 0.5

        # Each vertex moves in and out at a different rate.
        radius = base_radius + math.sin(elapsed * 3 + i * 1.5) * 100

        # Calculate the current vertex position.
        x = center_x + math.cos(angle) * radius
        y = center_y + math.sin(angle) * radius

        # Aim the bullet toward the centre.
        dx = center_x - x
        dy = center_y - y
        distance = math.hypot(dx, dy)

        if distance == 0:
            continue

        dx /= distance
        dy /= distance

        bullets.append(
            Bullet(x, y, dx, dy, speed=speed, radius=5)
        )

