import time
import pygame

from game.rules import (
    Player,
    Boss,
    check_collision,
    check_boss_collision,
    check_bullet_boss_collision,
    score_counter,
    handle_player_damage,
    use_bomb
)
from game.formations import (
    create_orbit_circle,
    fire_at_player,
    create_winder_wave,
    create_triangle_walls,
    create_geometry_pattern,
)

# --------------------
# Initialization
# --------------------

pygame.init()

pygame.mixer.music.load("assets/Sounds/govnovoz.mp3")
pygame.mixer.music.set_volume(1)  # Volume: 0.0–1.0
pygame.mixer.music.play(-1)         # -1 means loop forever

play_second_S = False

Play_third_S = False

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 800
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battle of Compensation")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 64)


button_font = pygame.font.Font(None, 44)

play_button = pygame.Rect(390, 350, 300, 70)
pause_button = pygame.Rect(950, 15, 110, 45)
resume_button = pygame.Rect(390, 350, 300, 70)
menu_button = pygame.Rect(390, 440, 300, 70)

username = ""
username_box = pygame.Rect(340, 290, 400, 50)
username_active = False

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

bomb_penalty = 0
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

phase4_start_time = None
last_geometry_time = 0

# --------------------
# Game loop
# --------------------

running = True
game_over = False
victory = False

game_state = "menu"  # menu, playing, paused

bomb_active = False
bomb_start_time = 0

while running:
    clock.tick(FPS)
    current_time = time.time()

    # Input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == "playing" and not game_over:
                    game_state = "paused"
                    pause_started_at = time.time()

                elif game_state == "paused":
                    game_state = "playing"

                    # Preserve attack timing after the pause.
                    paused_duration = time.time() - pause_started_at

                    last_boss_attack_time += paused_duration
                    last_winder_wave_time += paused_duration
                    pause_start_time += paused_duration
                    last_triangle_wall_time += paused_duration
                    last_aimed_shot_time += paused_duration
                    last_geometry_time += paused_duration

                    if phase3_start_time is not None:
                        phase3_start_time += paused_duration

                    if phase4_start_time is not None:
                        phase4_start_time += paused_duration


            elif event.key == pygame.K_x:
                if game_state == "playing" and not game_over:
                    if use_bomb(player, B_bullets):
                        bomb_penalty += 1000

                                

            

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos

                if game_state == "menu":
                    if play_button.collidepoint(mouse_pos):
                        game_state = "playing"

                elif game_state == "playing" and not game_over:
                    if pause_button.collidepoint(mouse_pos):
                        game_state = "paused"
                        pause_started_at = time.time()

                elif game_state == "paused":
                    if resume_button.collidepoint(mouse_pos):
                        game_state = "playing"

                        paused_duration = time.time() - pause_started_at

                        last_boss_attack_time += paused_duration
                        last_winder_wave_time += paused_duration
                        pause_start_time += paused_duration
                        last_triangle_wall_time += paused_duration
                        last_aimed_shot_time += paused_duration
                        last_geometry_time += paused_duration

                        if phase3_start_time is not None:
                            phase3_start_time += paused_duration

                        if phase4_start_time is not None:
                            phase4_start_time += paused_duration

        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "menu":
            username_active = username_box.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and game_state == "menu" and username_active:
            if event.key == pygame.K_BACKSPACE:
                username = username[:-1]

            elif event.key == pygame.K_RETURN:
                username_active = False
            elif event.unicode.isprintable() and len(username) < 16:
                username += event.unicode



    keys = pygame.key.get_pressed()

    dx = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
    dy = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
    focused = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]


    # --------------------
    # Game updates
    # --------------------

    if game_state == "playing" and not game_over:

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

        if hp_ratio <= 0.5 and not play_second_S:
            pygame.mixer.music.load("assets/Sounds/HUINYA.mp3")
            pygame.mixer.music.set_volume(3)
            pygame.mixer.music.play(-1)
            play_second_S = True

        if hp_ratio <= 0.25 and not Play_third_S:
            pygame.mixer.music.load("assets/Sounds/FNAF.mp3")
            pygame.mixer.music.set_volume(3)
            pygame.mixer.music.play(-1)
            Play_third_S = True

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

                fire_at_player(boss, player, B_bullets, speed=2.0)

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

        elif hp_ratio > 0.25:
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

            if current_time - last_aimed_shot_time >= AIMED_SHOT_INTERVAL:
                fire_at_player(boss, player, B_bullets, speed=8)
                last_aimed_shot_time = current_time

        else:
            if phase4_start_time is None:
                phase4_start_time = current_time

            elapsed = current_time - phase4_start_time

            GEOMETRY_INTERVAL = 0.12

            if current_time - last_geometry_time >= GEOMETRY_INTERVAL:
                create_geometry_pattern(
                    B_bullets,
                    boss.x,
                    boss.y,
                    elapsed,
                    vertex_count=6,
                    base_radius=200,
                    speed=5.0,
                )

                last_geometry_time = current_time


            # Occasional aimed shots keep the player moving.


        # --------------------
        # Player bullet collisions
        # --------------------

        for bullet in P_bullets[:]:
            if check_bullet_boss_collision(bullet, boss):
                boss.take_damage(player.damage)
                player.score += int(player.damage / boss.max_health * 100000)
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

    # Always draw the background first.
    screen.blit(field, (0, 0))

    # --------------------
    # Gameplay rendering
    # --------------------
    # Do not draw gameplay objects on the main menu.
    if game_state != "menu":

        # Player sprite
        screen.blit(
            player_model,
            (
                int(player.x - player_model.get_width() / 2),
                int(player.y - player_model.get_height() / 2),
            ),
        )

        # Boss sprite
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

        # HUD
        lives_text = font.render(
            f"Lives: {player.lives}",
            True,
            (255, 255, 255),
        )

        hp_text = font.render(
            f"Boss HP: {boss.healthPoints}",
            True,
            (255, 255, 255),
        )

        score_text = font.render(
            f"Score: {player.score}",
            True,
            (255, 255, 255),
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
                message,
                True,
                (255, 255, 255),
            )

            screen.blit(
                game_over_text,
                (
                    SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                    SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2,
                ),
            )

    # --------------------
    # Main menu — drawn last
    # --------------------
    if game_state == "menu":
        # The background was already drawn, and gameplay objects
        # were skipped, so the menu stays clean.
        title = large_font.render(
            "BATTLE OF COMPENSATION",
            True,
            (255, 255, 255),
        )

        screen.blit(
            title,
            (
                SCREEN_WIDTH // 2 - title.get_width() // 2,
                200,
            ),
        )

        pygame.draw.rect(screen, (40, 120, 70), play_button)
        pygame.draw.rect(screen, (255, 255, 255), play_button, 3)

        play_text = button_font.render(
            "PLAY",
            True,
            (255, 255, 255),
        )

        screen.blit(
            play_text,
            (
                play_button.centerx - play_text.get_width() // 2,
                play_button.centery - play_text.get_height() // 2,
            ),
        )
        username_label = font.render(
            "Enter username:",
            True,
            (255, 255, 255)
        )
        screen.blit(
            username_label,
            (username_box.x, username_box.y - 35)
        )

        # Username input box
        pygame.draw.rect(screen, (30, 30, 30), username_box)

        box_color = (255, 220, 100) if username_active else (220, 220, 220)
        pygame.draw.rect(screen, box_color, username_box, 3)

        # Text inside the box
        display_name = username if username else "Type your name..."
        text_color = (255, 255, 255) if username else (160, 160, 160)

        name_text = font.render(display_name, True, text_color)
        screen.blit(
            name_text,
            (username_box.x + 10, username_box.centery - name_text.get_height() // 2)
        )

    # --------------------
    # Pause screen — drawn over gameplay
    # --------------------
    elif game_state == "paused":
        overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.SRCALPHA,
        )

        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        paused_text = large_font.render(
            "PAUSED",
            True,
            (255, 255, 255),
        )

        screen.blit(
            paused_text,
            (
                SCREEN_WIDTH // 2 - paused_text.get_width() // 2,
                250,
            ),
        )

        pygame.draw.rect(screen, (40, 120, 70), resume_button)
        pygame.draw.rect(screen, (255, 255, 255), resume_button, 3)

        resume_text = button_font.render(
            "RESUME",
            True,
            (255, 255, 255),
        )

        screen.blit(
            resume_text,
            (
                resume_button.centerx - resume_text.get_width() // 2,
                resume_button.centery - resume_text.get_height() // 2,
            ),
        )

    # --------------------
    # Pause button — gameplay only
    # --------------------
    elif game_state == "playing" and not game_over:
        pygame.draw.rect(screen, (150, 40, 40), pause_button)
        pygame.draw.rect(screen, (255, 255, 255), pause_button, 2)

        pause_text = font.render(
            "PAUSE",
            True,
            (255, 255, 255),
        )

        screen.blit(
            pause_text,
            (
                pause_button.centerx - pause_text.get_width() // 2,
                pause_button.centery - pause_text.get_height() // 2,
            ),
        )

    # Present the completed frame once.
    pygame.display.flip()


pygame.quit()