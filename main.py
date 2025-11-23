import pygame
import random
import sys
import matplotlib as mpl
from PIL import Image

# --- Setup ---
pygame.init()

WIDTH, HEIGHT = 1400, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Famine Inc.")
background = pygame.image.load("map.jpeg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60

# --- map setup ---
MAX_ICONS = 10  
map_overlays = []
for i in range(1, MAX_ICONS + 1):
    path = f"map_images/{i}.png"
    try:
        img = pygame.image.load(path).convert_alpha()
    except Exception as e:
        print(f"[overlay] failed to load {path}: {e}")
        continue
    # tint to solid red while preserving per-pixel alpha
    red_img = img.copy()
    red_img.fill((255, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    red_img = pygame.transform.scale(red_img, (WIDTH, HEIGHT))
    # apply ~10% global opacity
    red_img.set_alpha(int(255 * 0.90))
    map_overlays.append(red_img)

# --- Data sets ---
agriculture_diseases=['Phytophthora infestans','Xanthomonas oryzae','Puccinia graminis','Fusarium oxysporum','Magnaporthe oryzae']
animal_diseases=['Foot-and-Mouth Disease','Avian Influenza','Bovine Tuberculosis','Swine Fever', 'Rinderpest']

# --- Player setup ---


# --- Game board setup ---
starter_disease=random.choice(agriculture_diseases + animal_diseases)
disease_type="Famine Disease" if starter_disease in agriculture_diseases else "Animal Disease"
country_of_origin=random.randint(0, 58)
countries=[100]*58
countries_coordinates=[]
for country in range(58):
    break
news=[f'New outbreak of {starter_disease} ({disease_type}) reported!']

# --- Food setup ---
hunger=100
health=100

 # ----------------------------------------
    #               BUTTON CLASS
    # ----------------------------------------

class Button:
    def __init__(self, rect, text, callback, bg=(200,200,200), fg=(0,0,0)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.bg = bg
        self.fg = fg

    def draw(self, surf, font):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos)
        color = tuple(max(0, c-30) for c in self.bg) if hovered else self.bg
        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        txt = font.render(self.text, True, self.fg)
        txt_rect = txt.get_rect(center=self.rect.center)
        surf.blit(txt, txt_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

 # ----------------------------------------
    #               BUTTON CLASS END
    # ----------------------------------------
# ----------------------------------------
#             NEWS TICKER
# ----------------------------------------

font = pygame.font.Font(None, 20)
font_small = pygame.font.Font(None, 22)
class NewsTicker:
    def __init__(self, rect, news_list, font, speed=80, fg=(255,255,0), bg=(0,0,0)):
        self.rect = pygame.Rect(rect)
        self.news = news_list
        self.font = font
        self.speed = speed  # pixels per second
        self.fg = fg
        self.bg = bg

        # join news with separator and prepare repeated surface for smooth loop
        self.sep = "   •   "
        self.base_text = self.sep.join(self.news) if self.news else ""
        if not self.base_text:
            self.base_text = "No news"
        # render a double-length surface so we can loop by sliding
        self.surface = self.font.render(self.base_text + self.sep + self.base_text, True, self.fg)
        self.base_width = self.font.size(self.base_text + self.sep)[0]
        self.surface_width = self.surface.get_width()
        self.offset = 0.0

    def refresh(self):
        # call when news list changes
        self.base_text = self.sep.join(self.news) if self.news else "No news"
        self.surface = self.font.render(self.base_text + self.sep + self.base_text, True, self.fg)
        self.base_width = self.font.size(self.base_text + self.sep)[0]
        self.surface_width = self.surface.get_width()
        self.offset = 0.0

    def update(self, dt):
        if self.base_width <= self.rect.width:
            # no need to scroll if the full text fits
            return
        self.offset += self.speed * dt
        # wrap offset so it never grows unbounded
        if self.offset >= self.base_width:
            self.offset -= self.base_width

    def draw(self, surf):
        # background bar
        pygame.draw.rect(surf, (50,50,50), self.rect)
        # clip drawing to the bar rect
        prev_clip = surf.get_clip()
        surf.set_clip(self.rect)

        y = self.rect.y + (self.rect.height - self.surface.get_height()) // 2
        x = self.rect.x - int(self.offset)
        # draw the double-length surface so sliding appears continuous
        surf.blit(self.surface, (x, y))
        # if needed draw an extra copy to cover the whole rect
        if x + self.surface_width < self.rect.x + self.rect.width:
            surf.blit(self.surface, (x + self.surface_width, y))


ticker_height = 30
news_ticker = NewsTicker((WIDTH/4, 0, WIDTH/2, ticker_height), news, font_small, speed=80, fg=(255,255,255))
# ----------------------------------------
#             NEWS TICKER END
# ----------------------------------------

newsImg = pygame.image.load("news.png")
newsImg = pygame.transform.scale(newsImg, (120, 120))

wfpButton = Button((0, HEIGHT, WIDTH/5, 100), "World Food Programme", lambda: None)
faoButton = Button((WIDTH/5, HEIGHT, WIDTH/5, 100), "Food and Agriculture Organization", lambda: None)

hungerButton = Button((4*(WIDTH/5), HEIGHT, WIDTH/5, 100), "Hunger", lambda: None)
healthButton = Button((3*(WIDTH/5), HEIGHT, WIDTH/5, 100), "Health", lambda: None)

    

# --- Game loop ---
running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # delta seconds

    # ----------------------------------------
    #             INPUT HANDLING
    # ----------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
        wfpButton.handle_event(event)
        faoButton.handle_event(event)
        healthButton.handle_event(event)
        hungerButton.handle_event(event)
            

            
    # ----------------------------------------
    #              GAME LOGIC
    # ----------------------------------------
    news_ticker.update(dt)

    # ----------------------------------------
    #               DRAWING
    # ----------------------------------------

    # Draw background
    screen.blit(background, (0, 0))
    for overlay in map_overlays:
        screen.blit(overlay, (0, 0))
        
        
        
    news_ticker.draw(screen)
    screen.blit(newsImg, (10, 0))
    
    

        
    wfpButton.draw(screen, font_small)
    faoButton.draw(screen, font_small)
    healthButton.draw(screen, font_small)
    hungerButton.draw(screen, font_small)



    # Draw menus
    # if menu is open, draw
    
   

    # Update display
    pygame.display.flip()

pygame.quit()