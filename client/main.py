import pygame
from game.rules import Player
from game.rules import Bullet
from game.rules import Boss

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)
clock = pygame.time.Clock()

player = Player(640, 480)
player_model = pygame.image.load("assets/Main_character_K (2).png").convert_alpha()
player_model = pygame.transform.scale(
    player_model,
    (48, 48)
)
boss = Boss(640, 100)
bullets = []
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    dx = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) \
       - int(keys[pygame.K_LEFT] or keys[pygame.K_a])

    dy = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) \
       - int(keys[pygame.K_UP] or keys[pygame.K_w])

    focused = (
        keys[pygame.K_LSHIFT]
        or keys[pygame.K_RSHIFT]
    )

    attack = (keys[pygame.K_z])

    player.move(dx, dy, focused)
    if attack:
        player.attack(bullets)
        pygame.draw.circle(
            screen,
            (255, 0, 0),
            (int(player.x), int(player.y)),
            player.bullet_radius
        )

    # Drawing belongs in the client
    screen.fill((15, 15, 25))
    screen.blit(
    player_model,
    (
        int(player.x - player_model.get_width() / 2),
        int(player.y - player_model.get_height() / 2)
    )
)

    pygame.draw.circle(screen,
        (255, 0, 0),
        (int(boss.x), int(boss.y)),
        boss.hitbox_radius
    )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()