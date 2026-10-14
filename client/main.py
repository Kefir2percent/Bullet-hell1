import time

import pygame

from game.rules import (
    Player,
    Bullet,
    Boss,
    check_collision,
    check_boss_collision,
    check_bullet_boss_collision,
    score_counter
)

from game.formations import create_orbit_circle
import game.formations

pygame.init()

# --------------------
# Settings
# --------------------

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 800
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bullet Hell")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 64)

# --------------------
# Game objects
# --------------------

player = Player(540, 600)
boss = Boss(540, 300)

player_model = pygame.image.load(
    "assets/Main_character_K (2).png"
).convert_alpha()
player_model = pygame.transform.scale(player_model, (48, 48))

boss_model = pygame.image.load(
    "assets/evil_boss1.png"
).convert_alpha()
boss_model = pygame.transform.scale(boss_model, (100, 100))

# Player bullets and boss bullets
P_bullets = []
B_bullets = []

create_orbit_circle(boss.x, boss.y, B_bullets)

running = True
game_over = False

last_boss_attack_time = 0
ring_time = 0
rotation_direction = 1

# --------------------
# Main game loop
# --------------------

while running:

    # 1. Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Read keyboard input
    keys = pygame.key.get_pressed()

    dx = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
    dy = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])

    focused = (
        keys[pygame.K_LSHIFT]
        or keys[pygame.K_RSHIFT]
    )

    # 3. Update the game if the player is alive
    if not game_over:

        # Player movement
        player.move(dx, dy, focused)

        # Player shooting
        if keys[pygame.K_z]:
            player.attack(P_bullets)

        # Update player bullets ONCE per frame
        player.update(P_bullets)

        # Update boss bullets ONCE per frame
        for bullet in B_bullets:
            bullet.update()


    current_time = time.time()
    hp_ratio = boss.healthPoints / boss.max_health

    if hp_ratio > 0.75:
        if current_time - last_boss_attack_time >= 0.6:

            create_orbit_circle(
                boss.x,
                boss.y,
                B_bullets,
                angular_speed=0.005 * rotation_direction
            )

            ring_time += 1
            last_boss_attack_time = current_time

            if ring_time >= 3:
                ring_time = 0
                rotation_direction *= -1

        # Remove boss bullets that leave the screen
        B_bullets[:] = [
            bullet for bullet in B_bullets
            if not bullet.is_off_screen()
        ]

        # Player bullets hitting the boss
        for bullet in P_bullets[:]:
            if check_bullet_boss_collision(bullet, boss):
                boss.take_damage(player.damage)
                P_bullets.remove(bullet)

        # Boss bullets hitting the player
        for bullet in B_bullets[:]:
            if check_collision(player, bullet):
                if not player.Invaluability:
                    player.take_damage()
                    B_bullets.remove(bullet)

                    if player.lives <= 0:
                        game_over = True
                else:
                    B_bullets.remove(bullet)

        # Update player invulnerability
        player.update_invulnerability()

        # Player touching the boss
        if (
            not player.Invaluability
            and check_boss_collision(player, boss)
        ):
            player.take_damage()

            # Move player away from the boss
            player.x = 640
            player.y = 480

            if player.lives <= 0:
                game_over = True

        if player.lives == 0 or boss.healthPoints <= 0:
            final_score = score_counter(player, boss)
            game_over = True

    # --------------------
    # Drawing
    # --------------------

    screen.fill((15, 15, 25))

    # Draw player and boss
    screen.blit(
        player_model,
        (
            int(player.x - player_model.get_width() / 2),
            int(player.y - player_model.get_height() / 2)
        )
    )


    screen.blit(
        boss_model,
        (
            int(boss.x - boss_model.get_width() / 2),
            int(boss.y - boss_model.get_height() / 2)
        )
    )

    # Draw player bullets
    for bullet in P_bullets:
        pygame.draw.circle(
            screen,
            (100, 200, 255),
            (int(bullet.x), int(bullet.y)),
            bullet.radius
        )

    # Draw boss bullets
    for bullet in B_bullets:
        pygame.draw.circle(
            screen,
            (255, 80, 80),
            (int(bullet.x), int(bullet.y)),
            bullet.radius
        )

    # Display player lives
    lives_text = font.render(
        f"Lives: {player.lives}",
        True,
        (255, 255, 255)
    )
    screen.blit(lives_text, (20, 20))

    # Display boss HP
    boss_hp_text = font.render(
        f"Boss HP: {boss.healthPoints}",
        True,
        (255, 255, 255)
    )

    score = int(score_counter(player, boss) * player.score_mult)
    score_text = font.render(
        f"Score: {score}",
        True,
        (255, 255, 255)
    )
    screen.blit(boss_hp_text, (20, 60))
    screen.blit(score_text, (20, 100))

    if focused:
        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (int(player.x), int(player.y)),
            player.hitbox_radius,
            0
        )



    # Game over message
    if game_over:
        game_over_text = large_font.render(
            "GAME OVER",
            True,
            (255, 60, 60)
        )

        screen.blit(
            game_over_text,
            (
                SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2
            )
        )

    # 4. Display the completed frame
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()