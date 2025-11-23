import pygame
import random
import sys


# --- Setup ---
pygame.init()

WIDTH, HEIGHT = 700, 360
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Famine Inc.")
background = pygame.image.load("map.jpeg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60

# --- Data sets ---
agriculture_diseases=['Phytophthora infestans','Xanthomonas oryzae','Puccinia graminis','Fusarium oxysporum','Magnaporthe oryzae']
animal_diseases=['Foot-and-Mouth Disease','Avian Influenza','Bovine Tuberculosis','Swine Fever', 'Rinderpest']

# --- Player setup ---


# --- Game board setup ---
starter_disease=random.choice(agriculture_diseases + animal_diseases)
disease_type="Famine Disease" if starter_disease in agriculture_diseases else "Animal Disease"
country_of_origin=random.randint(1, 58)
news=['New outbreak of {starter_disease} ({disease_type}) reported!']

# --- Food setup ---
hunger=100
health=100

# --- Button class ---
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

# --- Button class end

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
        pygame.draw.rect(surf, (10,10,10), self.rect)
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
news_ticker = NewsTicker((0, 0, WIDTH, ticker_height), news, font_small, speed=80, fg=(255,230,0))
# ----------------------------------------
#             NEWS TICKER END
# ----------------------------------------


# --- Game loop ---
running = True
while running:
    clock.tick(FPS)
    dt = clock.tick(FPS) / 1000.0  # delta seconds

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
    news_ticker.update(dt)

    # ----------------------------------------
    #               DRAWING
    # ----------------------------------------

    # Draw background
    screen.blit(background, (0, 0))

    newsButton = Button((10, 10, 200, 40), "News", lambda: print("\n".join(news)), bg=(100, 200, 100), fg=(255, 255, 255))

    # Draw menus
    # if menu is open, draw

    # Draw player and food

    # Draw score

    # Update display
    pygame.display.flip()

pygame.quit()
