import time
import pygame

from game.rules import (
    Player,
    Boss,
    check_collision,
    check_boss_collision,
    check_bullet_boss_collision,
    score_counter,
    handle_player_damage
)
from game.formations import (
    create_orbit_circle,
    fire_at_player,
    create_winder_wave,
    create_triangle_walls
)

# --------------------
# Initialization
# --------------------

pygame.init()

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 800
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bullet Hell")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 64)

field = pygame.image.load("assets/ogorod.png").convert()
field = pygame.transform.scale(field, (SCREEN_WIDTH, SCREEN_HEIGHT))

player_model = pygame.image.load(
    "assets/Main_character_K (2).png"
).convert_alpha()
player_model = pygame.transform.scale(player_model, (48, 48))

boss_model = pygame.image.load(
    "assets/evil_boss1.png"
).convert_alpha()
boss_model = pygame.transform.scale(boss_model, (100, 100))

player = Player(540, 600)
boss = Boss(540, 300)

STARTING_X = player.x
STARTING_Y = player.y

P_bullets = []
B_bullets = []

# --------------------
# Attack settings
# --------------------

ATTACK_INTERVAL = 0.6
PAUSE_DURATION = 2.0

last_boss_attack_time = time.time()
last_winder_wave_time = 0

ring_count = 0
rotation_direction = 1
burst_pause = False
pause_start_time = 0

winder_wave_count = 0
winder_direction = 1


# Phase 3: streaming walls
last_left_wall_time = 0
last_right_wall_time = 0
last_aimed_shot_time = 0

WALL_INTERVAL = 0.12
WALL_GAP_INTERVAL = 2.0
WALL_GAP_DURATION = 0.4
AIMED_SHOT_INTERVAL = 1.2

phase3_start_time = None
last_triangle_wall_time = 0
triangle_wall_count = 0

# --------------------
# Game loop
# --------------------

running = True
game_over = False
victory = False

while running:
    clock.tick(FPS)
    current_time = time.time()

    # Input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    dx = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
    dy = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
    focused = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

    # --------------------
    # Game updates
    # --------------------

    if not game_over:

        # Player movement and shooting
        player.move(dx, dy, focused)

        if keys[pygame.K_z]:
            player.attack(P_bullets)

        player.update(P_bullets)
        player.update_invulnerability()

        # Update enemy bullets
        for bullet in B_bullets:
            bullet.update()

        B_bullets[:] = [
            bullet for bullet in B_bullets
            if not bullet.is_off_screen()
        ]

        # --------------------
        # Boss attack phases
        # --------------------

        hp_ratio = boss.get_hp_ratio()

        if hp_ratio > 0.75:
            # Phase 1: orbiting rings and aimed shots
            if burst_pause:
                if current_time - pause_start_time >= PAUSE_DURATION:
                    burst_pause = False
                    rotation_direction *= -1
                    ring_count = 0

            elif current_time - last_boss_attack_time >= ATTACK_INTERVAL:
                create_orbit_circle(
                    boss.x,
                    boss.y,
                    B_bullets,
                    angular_speed=0.005 * rotation_direction,
                )

                fire_at_player(boss, player, B_bullets)

                ring_count += 1
                last_boss_attack_time = current_time

                if ring_count >= 3:
                    burst_pause = True
                    pause_start_time = current_time

        elif hp_ratio > 0.50:
            # Phase 2: Winder waves
            attack_interval = max(
                0.20,
                0.65 - winder_wave_count * 0.005,
            )

            if current_time - last_winder_wave_time >= attack_interval:
                create_winder_wave(
                    B_bullets,
                    count=12,
                    direction=winder_direction,
                    angle_offset=winder_wave_count * 0.12,
                    radius=15,
                )

                winder_wave_count += 1
                last_winder_wave_time = current_time

        else:
            # Phase 3: streaming walls
            if phase3_start_time is None:
                phase3_start_time = current_time

                # Keep the player horizontally inside the triangle.
                player.x = max(300, min(780, player.x))

            elapsed = current_time - phase3_start_time

            WALL_INTERVAL = 0.1
            WALL_GAP_INTERVAL = 2.0
            WALL_GAP_DURATION = 0.4
            AIMED_SHOT_INTERVAL = 0.1

            # Leave a short break between streams of triangles.
            gap_time = elapsed % WALL_GAP_INTERVAL
            gap_active = gap_time < WALL_GAP_DURATION

            # Spawn closed triangular walls.
            if (
                not gap_active
                and current_time - last_triangle_wall_time
                >= WALL_INTERVAL
            ):
                # Alternate the horizontal position slightly.
                offset = -50 if triangle_wall_count % 2 == 0 else 50
                center_x = 640 + offset

                create_triangle_walls(
                    B_bullets,
                    top_x=540,
                    top_y=300,
                    left_x=100,
                    right_x=1180,
                    bottom_y=800,
                    spacing=25,
                    speed=3.0,
                )

                triangle_wall_count += 1
                last_triangle_wall_time = current_time

            # Occasional aimed shots keep the player moving.
            if current_time - last_aimed_shot_time >= AIMED_SHOT_INTERVAL:
                fire_at_player(boss, player, B_bullets, speed=10)
                last_aimed_shot_time = current_time

        # --------------------
        # Player bullet collisions
        # --------------------

        for bullet in P_bullets[:]:
            if check_bullet_boss_collision(bullet, boss):
                boss.take_damage(player.damage)
                P_bullets.remove(bullet)

        # --------------------
        # Enemy bullet collisions
        # --------------------

        for bullet in B_bullets[:]:
            if check_collision(player, bullet):
                

                if not player.Invaluability:
                    player.take_damage()
                    handle_player_damage(player, B_bullets,STARTING_X,STARTING_Y)

                    B_bullets.remove

                    if player.lives <= 0:
                        game_over = True
                        
            continue

        # --------------------
        # Player and boss collision
        # --------------------

        if (
            not player.Invaluability
            and check_boss_collision(player, boss)
        ):
            player.take_damage()
            


            if player.lives <= 0:
                game_over = True

        # --------------------
        # Win / loss conditions
        # --------------------

        if boss.healthPoints <= 0:
            victory = True
            game_over = True

        elif player.lives <= 0:
            victory = False
            game_over = True

    # --------------------
    # Drawing
    # --------------------

    screen.blit(field, (0, 0))

    screen.blit(
        player_model,
        (
            int(player.x - player_model.get_width() / 2),
            int(player.y - player_model.get_height() / 2),
        ),
    )

    screen.blit(
        boss_model,
        (
            int(boss.x - boss_model.get_width() / 2),
            int(boss.y - boss_model.get_height() / 2),
        ),
    )

    # Player bullets
    for bullet in P_bullets:
        pygame.draw.circle(
            screen,
            (100, 200, 255),
            (int(bullet.x), int(bullet.y)),
            bullet.radius,
        )

    # Enemy bullets: support both colored diamonds and circles
    for bullet in B_bullets:
        x = int(bullet.x)
        y = int(bullet.y)
        radius = bullet.radius

        color = getattr(bullet, "color", (255, 255, 255))
        shape = getattr(bullet, "shape", "circle")

        if shape == "diamond":
            pygame.draw.polygon(
                screen,
                color,
                [
                    (x, y - radius),
                    (x + radius, y),
                    (x, y + radius),
                    (x - radius, y),
                ],
            )
        else:
            pygame.draw.circle(
                screen,
                color,
                (x, y),
                radius,
            )

    # UI
    lives_text = font.render(
        f"Lives: {player.lives}", True, (255, 255, 255)
    )
    hp_text = font.render(
        f"Boss HP: {boss.healthPoints}", True, (255, 255, 255)
    )

    score = int(score_counter(player, boss) * player.score_mult)
    score_text = font.render(
        f"Score: {score}", True, (255, 255, 255)
    )

    screen.blit(lives_text, (20, 20))
    screen.blit(hp_text, (20, 60))
    screen.blit(score_text, (20, 100))

    # Show the small hitbox while focused
    if focused and not game_over:
        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (int(player.x), int(player.y)),
            player.hitbox_radius,
        )

    # End screen
    if game_over:
        message = "YOU WIN!" if victory else "GAME OVER"

        game_over_text = large_font.render(
            message, True, (255, 255, 255)
        )

        screen.blit(
            game_over_text,
            (
                SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2,
            ),
        )

    pygame.display.flip()

pygame.quit()