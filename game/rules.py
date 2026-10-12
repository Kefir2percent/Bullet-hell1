import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
FPS = 60

# Colors (RGB)
BLACK = (15, 15, 25)
WHITE = (255, 255, 255)
PLAYER_COLOR = (0, 255, 128)
HITBOX_COLOR = (255, 50, 50)

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bullet Hell - Player Movement")
clock = pygame.time.Clock()

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.normal_speed = 5.0
        self.focus_speed = 2.5
        self.radius = 12  # Visual size of the player
        self.hitbox_radius = 3  # Tiny hitbox typical of bullet hells

    def handle_input(self):
        # Check if shift is held for focus/slow mode
        keys = pygame.key.get_pressed()
        current_speed = self.focus_speed if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else self.normal_speed

        # Calculate movement vector
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        # Normalize diagonal movement so player doesn't move faster diagonally
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        # Apply movement
        self.x += dx * current_speed
        self.y += dy * current_speed

        # Keep player within screen bounds
        self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.y))

    def draw(self, surface):
        # Draw outer visual body
        pygame.draw.circle(surface, PLAYER_COLOR, (int(self.x), int(self.y)), self.radius)
        
        # Draw precise center hitbox (crucial for bullet hell games)
        pygame.draw.circle(surface, HITBOX_COLOR, (int(self.x), int(self.y)), self.hitbox_radius)

# Initialize player at the bottom-center of the screen
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)

# Main Game Loop
while True:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 2. Update Game States
    player.handle_input()

    # 3. Drawing / Rendering
    screen.fill(BLACK)
    
    player.draw(screen)

    # Display instructions on screen
    font = pygame.font.SysFont(None, 24)
    instructions = font.render("Use WASD/Arrows to Move | Hold SHIFT for Focus Mode", True, WHITE)
    screen.blit(instructions, (20, 20))

    pygame.display.flip()

    # 4. Framerate Lock
    clock.tick(FPS)