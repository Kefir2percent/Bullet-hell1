import time
import random as r

# --------------------
# Game settings
# --------------------

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 800


# --------------------
# Player
# --------------------

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.score_mult = 1.0

        self.normal_speed = 5.0
        self.focus_speed = 2.5

        self.radius = 12
        self.hitbox_radius = 3

        self.damage = 50
        self.lives = 10

        self.attack_cooldown = 0.05
        self.last_attack_time = 0

        self.Invaluability = False
        self.Invaluability_duration = 1.0
        self.Invaluability_start_time = 0

    def move(self, dx, dy, focused):
        speed = self.focus_speed if focused else self.normal_speed

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.x += dx * speed
        self.y += dy * speed

        # Keep player inside the screen
        self.x = max(
            self.radius,
            min(SCREEN_WIDTH - self.radius, self.x)
        )
        self.y = max(
            self.radius,
            min(SCREEN_HEIGHT - self.radius, self.y)
        )

    def attack(self, bullets):
        current_time = time.time()

        if current_time - self.last_attack_time >= self.attack_cooldown:
            bullet = Bullet(self.x, self.y, 0, -1)
            bullets.append(bullet)
            self.last_attack_time = current_time

    def update(self, bullets):
        # Update each bullet once
        for bullet in bullets:
            bullet.update()

        # Remove bullets that have left the screen
        bullets[:] = [
            bullet for bullet in bullets
            if not bullet.is_off_screen()
        ]

    def take_damage(self):
        if self.Invaluability:
            return

        self.lives -= 1
        self.score_mult *= 0.75

        self.Invaluability = True
        self.Invaluability_start_time = time.time()

        print(f"Player took damage! Lives remaining: {self.lives}")
        

    def update_invulnerability(self):
        if self.Invaluability:
            current_time = time.time()

            if (
                current_time - self.Invaluability_start_time
                >= self.Invaluability_duration
            ):
                self.Invaluability = False

    def get_hitbox(self):
        return (self.x, self.y, self.hitbox_radius)

    def bullet_hitbox(self):
        return (self.x, self.y, self.radius)




# --------------------
# Bullet
# --------------------

class Bullet:
    def __init__(
        self, x, y, dx, dy,
        speed=10.0,
        radius=3
    ):
        self.x = x
        self.y = y

        self.dx = dx
        self.dy = dy

        self.speed = speed
        self.radius = radius

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

    def get_hitbox(self):
        return (self.x, self.y, self.radius)

# --------------------
# Boss
# --------------------

class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.radius = 60
        self.hitbox_radius = 60

        self.max_health = 200000
        self.healthPoints = self.max_health

        self.damage = 1

    def take_damage(self, damage):
        self.healthPoints = max(
            0,
            self.healthPoints - damage
        )

    def get_hitbox(self):
        return (self.x, self.y, self.hitbox_radius)

    def get_hp_ratio(self):
        return self.healthPoints / self.max_health


# --------------------
# Collision detection
# --------------------

def check_collision(player, bullet):
    """Check whether a bullet hits the player."""
    distance_squared = (
        (player.x - bullet.x) ** 2
        + (player.y - bullet.y) ** 2
    )

    radius_sum = player.hitbox_radius + bullet.radius

    return distance_squared < radius_sum ** 2


def check_bullet_boss_collision(bullet, boss):
    """Check whether a player bullet hits the boss."""
    distance_squared = (
        (bullet.x - boss.x) ** 2
        + (bullet.y - boss.y) ** 2
    )

    radius_sum = bullet.radius + boss.hitbox_radius

    return distance_squared < radius_sum ** 2


def check_boss_collision(player, boss):
    """Check whether the player touches the boss."""
    distance_squared = (
        (player.x - boss.x) ** 2
        + (player.y - boss.y) ** 2
    )

    radius_sum = player.hitbox_radius + boss.hitbox_radius

    return distance_squared < radius_sum ** 2


def score_counter(player, boss):
    """Calculate the score based on the boss's health."""
    player.score = int((1 - boss.get_hp_ratio()) * 100000)
    return player.score



def handle_player_damage(player, enemy_bullets, start_x, start_y):
    # Apply score penalty
    player.score_mult *= 0.75

    # Return player to starting position
    player.x = start_x
    player.y = start_y

    # Clear all enemy bullets
    enemy_bullets.clear()