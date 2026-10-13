import math
import time

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.normal_speed = 5.0
        self.focus_speed = 2.5
        self.radius = 12
        self.hitbox_radius = 3
        self.attack_cooldown = 0.05  # seconds
        self.last_attack_time = 0
        self.damage = 10

    def move(self, dx, dy, focused):
        current_speed = (
            self.focus_speed if focused
            else self.normal_speed
        )

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.x += dx * current_speed
        self.y += dy * current_speed

        # Keep player within screen bounds
        self.x = max(
            self.radius,
            min(SCREEN_WIDTH - self.radius, self.x)
        )
        self.y = max(
            self.radius,
            min(SCREEN_HEIGHT - self.radius, self.y)
        )
    def get_hitbox(self):
        return (self.x, self.y, self.hitbox_radius)

    def attack(self, bullets):
        current_time = time.time()

        if current_time - self.last_attack >= self.attack_cooldown:
            new_bullet = Bullet(self.x, self.y, 0, -1)
            bullets.append(new_bullet)
            self.last_attack = current_time

        def update(self, bullets):
            # Update bullets
            for bullet in bullets:
                bullet.update()

            # Remove off-screen bullets
            bullets[:] = [
                bullet for bullet in bullets
                if not bullet.is_off_screen()
            ]
        def bullet_hitbox(self):
            return (self.x, self.y, self.radius)

class Bullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.speed = 10.0
        self.radius = 3

    def update(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

    def is_off_screen(self):
        return (
            self.x < -self.radius or
            self.x > SCREEN_WIDTH + self.radius or
            self.y < -self.radius or
            self.y > SCREEN_HEIGHT + self.radius
        )
    def get_hitbox(self):
        return (self.x, self.y, self.radius)


def check_collision(player, bullet):
    distance_squared = (
        (player.x - bullet.x) ** 2
        + (player.y - bullet.y) ** 2
    )
    radius_sum = player.hitbox_radius + bullet.radius
    return distance_squared < radius_sum ** 2

def check_boss_collision(player, boss):
    distance_squared = (
        (player.x - boss.x) ** 2
        + (player.y - boss.y) ** 2
    )

    radius_sum = player.hitbox_radius + boss.hitbox_radius
    return distance_squared < radius_sum ** 2


class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 30
        self.hitbox_radius = 20
        self.healthPoints = 100000

    def get_hitbox(self):
        return (self.x, self.y, self.hitbox_radius)


    