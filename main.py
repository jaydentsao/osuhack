import pygame
import random

# --- Setup ---
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Starter Game Example")
pygame.display.set_background("51101cb559791d1372e717a865d9ae39.jpg")
clock = pygame.time.Clock()
FPS = 60

# --- Data sets ---
agriculture_diseases=['Phytophthora infestans','Xanthomonas oryzae','Puccinia graminis','Fusarium oxysporum','Magnaporthe oryzae']
animal_diseases=['Foot-and-Mouth Disease','Avian Influenza','Bovine Tuberculosis','Swine Fever', 'Rinderpest']

# --- Player setup ---
player_size = 40
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_speed = 5
player_color = (50, 200, 255)

# --- Game board setup ---
starter_disease=random.choice(agriculture_diseases + animal_diseases)
disease_type="Famine Disease" if starter_disease in agriculture_diseases else "Animal Disease"
news=['New outbreak of {starter_disease} ({disease_type}) reported!']

# --- Food setup ---
hunger=100
health=100


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
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
    # ----------------------------------------
    #              GAME LOGIC
    # ----------------------------------------


    # ----------------------------------------
    #               DRAWING
    # ----------------------------------------

    # Draw background
    screen.fill((20, 20, 20))

    # Draw map
    

    # Draw buttons

    # Update display
    pygame.display.flip()

pygame.quit()
