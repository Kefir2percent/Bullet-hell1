import pygame
from game.rules import Player
from game.rules import Bullet
from game.rules import Boss

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800

G_FIELD_X = 960
G_FIELD_Y = 800

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)
clock = pygame.time.Clock()

player = Player(640, 480)
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
            player.bullet_hitbox()[2]
        )
        player.update(bullets)

    # Drawing belongs in the client
    gamefield = pygame.image.load("assets/derevenskij-ogorod.jpg").convert()
    gamefield = pygame.transform.scale(
    gamefield,
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)
    screen.blit(gamefield, (G_FIELD_X, G_FIELD_Y))
    screen.fill((15, 15, 25))
    pygame.draw.circle(
        screen,
        (0, 255, 128),
        (int(player.x), int(player.y)),
        player.radius
    )

    pygame.draw.circle(
        screen,
        (255, 0, 0),
        (int(boss.x), int(boss.y)),
        boss.hitbox_radius
    )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
