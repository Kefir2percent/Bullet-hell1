import math

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
        # Example attack: shoot a bullet straight up
        bullet_dx = 0
        bullet_dy = -1
        new_bullet = Bullet(self.x, self.y, bullet_dx, bullet_dy)
        bullets.append(new_bullet)

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
    distance = math.sqrt(
        (player.x - bullet.x) ** 2 +
        (player.y - bullet.y) ** 2
    )

    return distance < (player.hitbox_radius + bullet.radius)

class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 30
        self.hitbox_radius = 20

    def get_hitbox(self):
        return (self.x, self.y, self.hitbox_radius)


    