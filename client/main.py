
import time
import pygame

from game.rules import (
    Player,
    Boss,
    check_collision,
    check_boss_collision,
    check_bullet_boss_collision,
    score_counter
)

from game.formations import (
    create_orbit_circle,
    fire_at_player,
    create_winder_wave
)

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
# Background
# --------------------

field = pygame.image.load("assets/ogorod.png")
field = pygame.transform.scale(
    field,
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

# --------------------
# Game objects
# --------------------

player = Player(540, 600)
STARTING_X = player.x
STARTING_Y = player.y

boss = Boss(540, 300)

# Original character models
player_model = pygame.image.load(
    "assets/Main_character_K (2).png"
).convert_alpha()

player_model = pygame.transform.scale(
    player_model,
    (48, 48)
)

boss_model = pygame.image.load(
    "assets/evil_boss1.png"
).convert_alpha()

boss_model = pygame.transform.scale(
    boss_model,
    (100, 100)
)

# --------------------
# Bullets
# --------------------

P_bullets = []
B_bullets = []

create_orbit_circle(
    boss.x,
    boss.y,
    B_bullets
)

# --------------------
# Game state
# --------------------

running = True
game_over = False
final_score = 0

# --------------------
# Orbit attack settings
# --------------------

ring_time = 0
rotation_direction = 1

last_boss_attack_time = 0
burst_pause = False
pause_start_time = 0

ATTACK_INTERVAL = 0.6
PAUSE_DURATION = 2.0

# --------------------
# Winder attack settings
# --------------------

winder_start_time = time.time()
last_winder_wave_time = 0

winder_wave_count = 0
winder_direction = 1

# Track the current attack phase.
current_phase = 1

# ==================================================
# MAIN GAME LOOP
# ==================================================

while running:

    clock.tick(FPS)
    current_time = time.time()

    # --------------------
    # 1. Handle events
    # --------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # --------------------
    # 2. Read keyboard input
    # --------------------

    keys = pygame.key.get_pressed()

    dx = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
    dy = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])

    focused = (
        keys[pygame.K_LSHIFT]
        or keys[pygame.K_RSHIFT]
    )

    # ==================================================
    # 3. UPDATE GAME
    # ==================================================

    if not game_over:

        # --------------------
        # Player movement
        # --------------------

        player.move(dx, dy, focused)

        # --------------------
        # Player shooting
        # --------------------

        if keys[pygame.K_z]:
            player.attack(P_bullets)

        # Updates and cleans up player bullets.
        player.update(P_bullets)

        # --------------------
        # Update boss bullets
        # --------------------

        for bullet in B_bullets:
            bullet.update()

        # Remove bullets that leave the screen.
        B_bullets[:] = [
            bullet for bullet in B_bullets
            if not bullet.is_off_screen()
        ]

        # --------------------
        # Determine attack phase
        # --------------------

        hp_ratio = boss.get_hp_ratio()

        # Switch phases only once.
        # Clear the old pattern when entering Winder.
        if hp_ratio <= 0.75 and current_phase == 1:

            current_phase = 2
            B_bullets.clear()

            winder_start_time = current_time
            last_winder_wave_time = 0
            winder_wave_count = 0
            winder_direction = 1

        # ==================================================
        # PHASE 1: ORBIT RINGS
        # ==================================================

        if current_phase == 1:

            if burst_pause:

                if current_time - pause_start_time >= PAUSE_DURATION:

                    burst_pause = False
                    rotation_direction *= -1
                    ring_time = 0

            else:

                if current_time - last_boss_attack_time >= ATTACK_INTERVAL:

                    create_orbit_circle(
                        boss.x,
                        boss.y,
                        B_bullets,
                        angular_speed=0.005 * rotation_direction
                    )

                    fire_at_player(
                        boss,
                        player,
                        B_bullets
                    )

                    ring_time += 1
                    last_boss_attack_time = current_time

                    # Pause after three rings.
                    if ring_time >= 3:

                        burst_pause = True
                        pause_start_time = current_time

        # ==================================================
        # PHASE 2: RAINBOW WINDER
        # ==================================================

        elif current_phase == 2:

            elapsed = current_time - winder_start_time

            # Waves gradually become more frequent.
            attack_interval = max(
                0.20,
                0.65 - elapsed * 0.005
            )

            if current_time - last_winder_wave_time >= attack_interval:

                create_winder_wave(
                    B_bullets,
                    count=12,
                    direction=winder_direction,
                    angle_offset=winder_wave_count * 0.12
                )

                winder_wave_count += 1
                last_winder_wave_time = current_time

                # Reverse direction periodically.
                if winder_wave_count in (6, 12, 18):
                    winder_direction *= -1

        # ==================================================
        # PLAYER BULLETS HIT BOSS
        # ==================================================

        for bullet in P_bullets[:]:

            if check_bullet_boss_collision(bullet, boss):

                boss.take_damage(player.damage)
                P_bullets.remove(bullet)

        # ==================================================
        # BOSS BULLETS HIT PLAYER
        # ==================================================

        for bullet in B_bullets[:]:

            if check_collision(player, bullet):

                # Remove the bullet on contact.
                B_bullets.remove(bullet)

                if not player.Invaluability:
                    player.take_damage()

        # ==================================================
        # PLAYER TOUCHES BOSS
        # ==================================================

        if (
            not player.Invaluability
            and check_boss_collision(player, boss)
        ):

            player.take_damage()

            # Move the player away from the boss.
            player.x = 640
            player.y = 480

        # ==================================================
        # INVULNERABILITY
        # ==================================================

        player.update_invulnerability()

        # ==================================================
        # WIN / LOSS CONDITIONS
        # ==================================================

        if player.lives <= 0 or boss.healthPoints <= 0:

            final_score = int(
                score_counter(player, boss) * player.score_mult
            )

            game_over = True

    # ==================================================
    # 4. DRAWING
    # ==================================================

    screen.blit(field, (0, 0))

    # --------------------
    # Draw original player model
    # --------------------

    screen.blit(
        player_model,
        (
            int(player.x - player_model.get_width() / 2),
            int(player.y - player_model.get_height() / 2)
        )
    )

    # --------------------
    # Draw original boss model
    # --------------------

    screen.blit(
        boss_model,
        (
            int(boss.x - boss_model.get_width() / 2),
            int(boss.y - boss_model.get_height() / 2)
        )
    )

    # --------------------
    # Draw player bullets
    # --------------------

    for bullet in P_bullets:

        pygame.draw.circle(
            screen,
            (100, 200, 255),
            (int(bullet.x), int(bullet.y)),
            bullet.radius
        )

    # --------------------
    # Draw boss bullets
    # --------------------

    for bullet in B_bullets:

        x = int(bullet.x)
        y = int(bullet.y)
        radius = bullet.radius

        # Ordinary Bullet objects may not have a color attribute.
        color = getattr(
            bullet,
            "color",
            (255, 255, 255)
        )

        shape = getattr(
            bullet,
            "shape",
            "circle"
        )

        if shape == "diamond":

            pygame.draw.polygon(
                screen,
                color,
                [
                    (x, y - radius),
                    (x + radius, y),
                    (x, y + radius),
                    (x - radius, y)
                ]
            )

        else:

            pygame.draw.circle(
                screen,
                color,
                (x, y),
                radius
            )

    # --------------------
    # Display player lives
    # --------------------

    lives_text = font.render(
        f"Lives: {player.lives}",
        True,
        (255, 255, 255)
    )

    screen.blit(lives_text, (20, 20))

    # --------------------
    # Display boss HP
    # --------------------

    boss_hp_text = font.render(
        f"Boss HP: {boss.healthPoints}",
        True,
        (255, 255, 255)
    )

    screen.blit(boss_hp_text, (20, 60))

    # --------------------
    # Display score
    # --------------------

    score = int(
        score_counter(player, boss) * player.score_mult
    )

    score_text = font.render(
        f"Score: {score}",
        True,
        (255, 255, 255)
    )

    screen.blit(score_text, (20, 100))

    # --------------------
    # Focused-mode hitbox indicator
    # --------------------

    if focused:

        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (int(player.x), int(player.y)),
            player.hitbox_radius,
            0
        )

    # ==================================================
    # GAME OVER
    # ==================================================

    if game_over:

        overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        if boss.healthPoints <= 0:
            message = "VICTORY!"
            message_color = (255, 220, 80)
        else:
            message = "GAME OVER"
            message_color = (255, 255, 255)

        game_over_text = large_font.render(
            message,
            True,
            message_color
        )

        screen.blit(
            game_over_text,
            (
                SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2
            )
        )

        final_score_text = font.render(
            f"Final score: {final_score}",
            True,
            (255, 255, 255)
        )

        screen.blit(
            final_score_text,
            (
                SCREEN_WIDTH // 2 - final_score_text.get_width() // 2,
                SCREEN_HEIGHT // 2 + 50
            )
        )

    # --------------------
    # Display completed frame
    # --------------------

    pygame.display.flip()

# ==================================================
# QUIT
# ==================================================

pygame.quit()
