import pygame
import random

# --- Setup ---
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Starter Game Example")

clock = pygame.time.Clock()
FPS = 60

# --- Player setup ---
player_size = 40
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_speed = 5
player_color = (50, 200, 255)

# --- Food setup ---
food_size = 30
food_x = random.randint(0, WIDTH - food_size)
food_y = random.randint(0, HEIGHT - food_size)
food_color = (255, 180, 0)

score = 0

# --- Game loop ---
running = True
while running:
    clock.tick(FPS)

    # ----------------------------------------
    #             INPUT HANDLING
    # ----------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Movement input
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_x += player_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_y -= player_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_y += player_speed

    # Prevent going off-screen
    player_x = max(0, min(WIDTH - player_size, player_x))
    player_y = max(0, min(HEIGHT - player_size, player_y))

    # ----------------------------------------
    #              GAME LOGIC
    # ----------------------------------------
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    food_rect = pygame.Rect(food_x, food_y, food_size, food_size)

    # Collision check
    if player_rect.colliderect(food_rect):
        score += 1
        food_x = random.randint(0, WIDTH - food_size)
        food_y = random.randint(0, HEIGHT - food_size)

    # ----------------------------------------
    #               DRAWING
    # ----------------------------------------
    screen.fill((20, 20, 20))  # background

    # Draw player and food
    pygame.draw.rect(screen, player_color, player_rect)
    pygame.draw.rect(screen, food_color, food_rect)

    # Draw score
    font = pygame.font.SysFont(None, 40)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    # Update display
    pygame.display.flip()

pygame.quit()
