import pygame
import random

# --- Setup ---
pygame.init()

WIDTH, HEIGHT = 1400, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Famine Inc.")
background = pygame.image.load("map.jpeg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60

pending_action = None
all_action = None


# --- map setup ---
MAX_ICONS = 57  
map_overlays = []
map_masks = []
for i in range(0, MAX_ICONS + 1):
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
    red_img.set_alpha(int(255 * 0))
    map_overlays.append(red_img)
    map_masks.append(pygame.mask.from_surface(red_img))

# build a single ID map surface (each country -> unique color)
# color encoding: (index+1, 0, 0) so 0 means "no country"
id_map = pygame.Surface((WIDTH, HEIGHT), flags=pygame.SRCALPHA).convert_alpha()
id_map.fill((0,0,0,0))
for idx, mask in enumerate(map_masks):
    # mask.to_surface paints setcolor where mask present
    surf = mask.to_surface(setcolor=(idx + 1, 0, 0, 255), unsetcolor=(0, 0, 0, 0))
    id_map.blit(surf, (0, 0))

hover_highlights = []
for mask in map_masks:
    # create a single, reusable highlight surface (soft gray + alpha)
    surf = mask.to_surface(setcolor=(220, 220, 220, 160), unsetcolor=(0, 0, 0, 0)).convert_alpha()
    hover_highlights.append(surf)

# --- Data sets ---
agriculture_diseases=['Phytophthora infestans','Xanthomonas oryzae','Puccinia graminis','Fusarium oxysporum','Magnaporthe oryzae']
animal_diseases=['Foot-and-Mouth Disease','Avian Influenza','Bovine Tuberculosis','Swine Fever', 'Rinderpest']

# --- Player setup ---


# --- Game board setup ---
starter_disease=random.choice(agriculture_diseases + animal_diseases)
disease_type="Agricultural Disease" if starter_disease in agriculture_diseases else "Animal Disease"
country_of_origin=random.randint(0, 58)
infected_countries=[country_of_origin]
initial_spread=random.randint(0,2)

country_fed=[True]*58
country_famine=[70]*58
country_health=[30]*58
country_names = {
    0: "Argentina",
    1: "Bolivia",
    2: "Peru",
    3: "Brazil",
    4: "Columbia",
    5: "Caribbean",
    6: "Central America",
    7: "Mexico",
    8: "USA",
    9: "Canada",
    10: "Greenland",
    11: "Iceland",
    12: "UK",
    13: "France",
    14: "Australia",
    15: "New Guinea",
    16: "Philippines",
    17: "New Zealand",
    18: "Indonesia",
    19: "South East Asia",
    20: "Japan",
    21: "China",
    22: "Korea",
    23: "Russia",
    24: "India",
    25: "Afghanistan",
    26: "Pakistan",
    27: "Central Asia",
    28: "Kazakhstan",
    29: "Saudi Arabia",
    30: "Iran", 
    31: "Iraq",
    32: "Turkey",
    33: "Middle East",
    34: "Morocco",
    35: "Algeria",
    36: "Libya",
    37: "Egypt",
    38: "Sudan",
    39: "West Africa",
    40: "Central Africa",
    41: "East Africa",
    42: "South Africa",
    43: "Botswana",
    44: "Zimbabwe",
    45: "Angola",
    46: "Madagascar",
    47: "Finland",
    48: "Sweden",
    49: "Norway",
    50: "Spain",
    51: "Italy",
    52: "Germany",
    53: "Central Europe",
    54: "Balkan States",
    55: "Baltic States",
    56: "Ukraine",
    57: "Poland"
}
countries_neighbors={
    0:  [1, 3],                                # Argentina
    1:  [0, 2, 3],                             # Bolivia
    2:  [1, 4]    ,                               # Peru
    3:  [0, 1, 4, 39]      ,                      # Brazil
    4:  [2, 3, 5, 6]    ,                         # Colombia
    5:  [4, 6, 7]         ,                       # Caribbean (close to Mexico)
    6:  [5, 7]           ,                        # Central America
    7:  [6, 5, 8]          ,                      # Mexico
    8:  [7, 9]           ,                        # USA
    9:  [8, 10]           ,                        # Canada
    10: [9, 11, 49]          ,                     # Greenland (close to Iceland & Norway coast)
    11: [10, 12, 50]         ,                    # Iceland (close to UK & Spain)
    12: [11, 13, 50]        ,                     # UK (Channel + Atlantic)
    13: [12, 50, 51, 52]       ,                   # France
    14: [15, 18, 17]           ,                   # Australia (close to NG, Indonesia, NZ)
    15: [14, 18]               ,                   # New Guinea
    16: [18, 19, 21]            ,                  # Philippines
    17: [14]                     ,                 # New Zealand
    18: [14, 15, 16, 19]          ,                # Indonesia
    19: [16, 18, 21, 24]           ,               # SE Asia (China/India proximity)
    20: [21, 22, 23]                ,              # Japan (near China & Russia too)
    21: [22, 23, 24, 19, 20]         ,             # China
    22: [20, 21, 23]                  ,            # Korea
    23: [21, 22, 47, 48, 49, 56, 28, 20],          # Russia (Japan, China, Korea, Nordics)
    24: [21, 19, 25, 26]                 ,         # India
    25: [24, 26, 27, 30, 31]              ,        # Afghanistan
    26: [24, 25, 30]                       ,       # Pakistan
    27: [25, 28, 21]                        ,      # Central Asia
    28: [27, 23, 56]                         ,     # Kazakhstan
    29: [30, 31, 33, 37]                        ,  # Saudi Arabia
    30: [29, 25, 26, 31, 32]                     , # Iran
    31: [29, 30, 32, 33, 37]                    ,  # Iraq
    32: [30, 31, 33, 54, 56]    ,                  # Turkey
    33: [29, 31, 32, 37]        ,                  # Middle East
    34: [35, 39, 50]             ,                 # Morocco (close to Spain)
    35: [34, 36]                  ,                # Algeria
    36: [35, 37]                   ,               # Libya
    37: [36, 31, 29, 33, 38, 50]    ,              # Egypt (Mediterranean adjacency to Europe)
    38: [37, 40, 41]                 ,             # Sudan
    39: [34, 40, 3]                   ,            # West Africa
    40: [39, 41, 45]                   ,           # Central Africa
    41: [38, 40, 42, 44, 45]            ,          # East Africa
    42: [41, 43, 44]                     ,         # South Africa
    43: [42, 44]                          ,        # Botswana
    44: [43, 42, 41]                       ,       # Zimbabwe
    45: [40, 41]                            ,      # Angola
    46: [41]                                 ,     # Madagascar (closest to East Africa)
    47: [23, 48, 55]                          ,    # Finland
    48: [47, 49, 55, 52]                ,          # Sweden
    49: [48, 23, 10]                     ,         # Norway (close to Greenland)
    50: [13, 12, 11, 34, 37]                ,      # Spain (Mediterranean + Morocco)
    51: [13, 50, 52, 54]                  ,        # Italy
    52: [13, 51, 53, 48, 56, 57]          ,        # Germany
    53: [52, 54, 57, 56]                   ,       # Central Europe
    54: [32, 51, 53, 57]                  ,        # Balkan States
    55: [47, 48, 49, 23, 56]              ,        # Baltic States
    56: [28, 23, 32, 52, 53, 55, 57]     ,         # Ukraine
    57: [52, 53, 54, 56]                ,          # Poland
}
game_won=False
for i in range(initial_spread):
    neighbors=countries_neighbors.get(random.choice(infected_countries))
    num_infected=random.randint(0, len(neighbors))
    while num_infected>0:
        new_infected=random.choice(neighbors)
        if new_infected not in infected_countries:
            infected_countries.append(new_infected)
            num_infected-=1
        if neighbors in infected_countries:
            break

infected_names = []
for i in infected_countries:
    country_fed[i] = False
    country_famine[i] = random.randint(20, 60)
    infected_names.append(country_names.get(i, f"Unknown ({i})"))
infected_names_str = ", ".join(infected_names) if infected_names else "Unknown"
news = [f'Famine detected in {infected_names_str}!']


budget = 10000000000  # 10 billion starting budget
MAX_PROFIT = 300_000_000  # profit per second when average health == 100%
budget_acc = 0.0

# --- Food setup ---
hunger=100
health=100

 # ----------------------------------------
    #               BUTTON CLASS
    # ----------------------------------------

class Button:
    def __init__(self, rect, text, callback, bg=(200, 200, 200), fg=(0, 0, 0), text_below=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.bg = bg
        self.fg = fg
        self.text_below = text_below  # New attribute for text below the button
        self._cached_text = None
        self._cached_surface = None
        self._cached_below_surface = None
        
    def draw(self, surf, font):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos)
        color = tuple(max(0, min(255, c - 50)) for c in self.bg) if hovered else self.bg
        pygame.draw.rect(surf, color, self.rect, border_radius=6)

        # Split the text into lines
        lines = self.text.splitlines()
        line_height = font.get_linesize()

        # Render each line
        for i, line in enumerate(lines):
            if line != self._cached_text or self._cached_surface is None:
                self._cached_text = line
                self._cached_surface = font.render(line, True, self.fg)
            txt = self._cached_surface
            txt_rect = txt.get_rect(center=(self.rect.centerx, self.rect.y + 10 + i * line_height))
            surf.blit(txt, txt_rect)

        # Render the text below the button
        if self.text_below:
            if self.text_below != self._cached_below_surface:
                self._cached_below_surface = font.render(self.text_below, True, self.fg)
            below_txt = self._cached_below_surface
            below_txt_rect = below_txt.get_rect(center=(self.rect.centerx, self.rect.bottom + 10))
            surf.blit(below_txt, below_txt_rect)
    

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
        if self.base_width == 0:
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

        # restore previous clip so other UI (buttons/hover states) render correctly
        surf.set_clip(prev_clip)


ticker_height = 30
news_ticker = NewsTicker((WIDTH/4, 0, WIDTH/2, ticker_height), news, font_small, speed=80, fg=(255,255,255))
# ----------------------------------------
#             NEWS TICKER END
# ----------------------------------------

# ----------------------------------------
#             POPUP START
# ----------------------------------------
class Popup:
    def __init__(self, rect, title, text, font):
        self.rect = pygame.Rect(rect)
        self.title = title
        self.text = text
        self.font = font
        self.active = False
        self.bg = (240, 240, 240)
        self.fg = (0, 0, 0)
        self.buttons = []

    def show(self, title=None, text=None, buttons=None, pos=None):
        if title is not None:
            self.title = title
        if text is not None:
            self.text = text
        if buttons is not None:
            self.buttons = buttons
        if pos is not None:
            # keep popup fully on-screen
            x = max(0, min(WIDTH - self.rect.width, int(pos[0])))
            y = max(0, min(HEIGHT - self.rect.height, int(pos[1])))
            self.rect.topleft = (x, y)
        self.active = True

    def hide(self):
        self.active = False

    def draw(self, surf):
        if not self.active:
            return
        # dark overlay
        overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surf.blit(overlay, (0, 0))

        # popup box
        pygame.draw.rect(surf, self.bg, self.rect, border_radius=8)
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 2, border_radius=8)

        title_s = self.font.render(self.title, True, self.fg)
        surf.blit(title_s, (self.rect.x + 12, self.rect.y + 10))

        # simple one-line body (wrap if needed)
        y_off = self.rect.y + 40
        for i, line in enumerate(self.text.splitlines()):
            body_s = self.font.render(line, True, self.fg)
            surf.blit(body_s, (self.rect.x + 12, y_off + i * self.font.get_linesize()))


        # draw popup buttons
        for b in self.buttons:
            b.draw(surf, self.font)

    def handle_event(self, event):
        if not self.active:
            return False
        # close popup on ESC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.hide()
            return True
        # if click outside popup, close and consume event
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.rect.collidepoint(event.pos):
                self.hide()
                return True
        for b in self.buttons:
            b.handle_event(event)
        return True
    
def make_close_button(popup):
    btn = Button((popup.rect.right - 90, popup.rect.bottom - 48, 80, 32), "Close", lambda: popup.hide())
    popup.buttons = [btn]
    return btn  
    
popup_rect = ((WIDTH//4), (HEIGHT//4), WIDTH/2, HEIGHT/2)
popup_wfp   = Popup(popup_rect, "World Food Programme", "WFP information...", font_small)
popup_fao   = Popup(popup_rect, "Food and Agriculture Organization", "FAO information...", font_small)
popup_country = Popup((WIDTH//2 - 200, HEIGHT//2 - 120, 400, 200), "Country", "Info", font_small)

close_wfp = make_close_button(popup_wfp)
close_fao = make_close_button(popup_fao)

# ----------------------------------------
#             POPUP  END
# ----------------------------------------



# --- Info Box Setup ---

class InfoBox:
    def __init__(self, rect, text, bg=(200,200,200), fg=(0,0,0)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bg = bg
        self.fg = fg
        self._cached_text = None
        self._cached_surface = None
    
    def draw(self, surf, font):
        # draw without hover darkening so appearance stays constant
        pygame.draw.rect(surf, self.bg, self.rect, border_radius=6)
        if self.text != self._cached_text or self._cached_surface is None:
            self._cached_text = self.text
            self._cached_surface = font.render(self.text, True, self.fg)
        txt = self._cached_surface
        txt_rect = txt.get_rect(center=self.rect.center)
        surf.blit(txt, txt_rect)

# --- Info Box End ---

class Textbox:
    def __init__(self, rect, font, text="", bg=(255, 255, 255), fg=(0, 0, 0), border_color=(0, 0, 0)):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.text = text
        self.bg = bg
        self.fg = fg
        self.border_color = border_color
        self.active = False  # Whether the textbox is focused for input
        self._cached_surface = None

    def draw(self, surf):
        # Draw the textbox background
        pygame.draw.rect(surf, self.bg, self.rect)
        # Draw the border
        pygame.draw.rect(surf, self.border_color, self.rect, 2)
        # Render the text
        if self._cached_surface is None or self.text != self._cached_surface:
            self._cached_surface = self.font.render(self.text, True, self.fg)
        text_surface = self._cached_surface
        text_rect = text_surface.get_rect(topleft=(self.rect.x + 5, self.rect.y + 5))
        surf.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the textbox is clicked
            self.active = self.rect.collidepoint(event.pos)
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                # Remove the last character
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                # Handle "Enter" key (optional: submit the text)
                self.active = False
            else:
                # Add the typed character
                self.text += event.unicode

newsImg = pygame.image.load("news.png")
newsImg = pygame.transform.scale(newsImg, (ticker_height, ticker_height))

wfpButton = Button((0, HEIGHT-100, WIDTH/5, 100), "World Food Programme", lambda: popup_wfp.show(title=popup_wfp.title, text=popup_wfp.text, buttons=popup_wfp.buttons))
#airdropButton = Button((, HEIGHT-100, WIDTH/5, 100), "Airdrop Food", lambda: None)

faoButton = Button((WIDTH/5, HEIGHT-100, WIDTH/5, 100), "Food and Agriculture Organization",  lambda: popup_fao.show(title=popup_fao.title, text=popup_fao.text, buttons=popup_fao.buttons))

wfpButton.callback = lambda pop=popup_wfp: pop.show(title=pop.title, text=pop.text, buttons=[wfpbutton1, wfpbutton2, wfpbutton3])
faoButton.callback = lambda: (popup_fao.show(title=popup_fao.title, text=popup_fao.text, buttons=[faobutton1, faobutton2, faobutton3]), )

healthBox = InfoBox((3*(WIDTH/5), HEIGHT-100, WIDTH/5, 100), f"Health: --", bg=(200,200,200))
hungerBox = InfoBox((4*(WIDTH/5), HEIGHT-100, WIDTH/5, 100), f"Hunger: --", bg=(200,200,200))




def apply_action(action_name):
    global pending_action
    pending_action = action_name  # Set the pending action
    
# ...existing code...
def apply_action_to_country(action_name, country_index,budget)->int:
    if action_name == "Rapidly Airdrop Food to Selected Country" and budget >= 1500000000:
        country_famine[country_index] = min(70,country_famine[country_index]+40)  # Reduce famine level
        return budget-1500000000  # Deduct cost
    elif action_name == "Ship Food to Selected Country" and budget >= 750000000:
        country_famine[country_index] = min(70,country_famine[country_index]+20)  # Reduce famine level
        return budget-750000000  # Deduct cost
    elif action_name == "Distribute Food to Countries in Need" and budget >= 3000000000:  # Deduct cost
        for i in range(58):
            country_famine[i] = min(70,country_famine[i]+20)  # Reduce famine level
        return budget-3000000000
    
    elif action_name == "Subsidize Farming" and budget >= 1500000000:
        country_health[country_index] = min(30,country_health[country_index]+20)  # Increase health level
        return budget-1500000000  # Deduct cost
        
    elif action_name == "Cure Plant/Animal Disease in Selected Country" and budget >= 7500000000 and country_index in infected_countries:
        infected_countries.remove(country_index) # Increase health level
        return budget-7500000000  # Deduct cost
        
    elif action_name == "Implement Global Agricultural Practice Programs" and budget >= 2000000000:
        for i in range(58):
            country_famine[i] = min(30,country_famine[i]+10)  # Reduce famine level
        return budget-2000000000  # Deduct cost
    
    
    return budget

faobutton1 = Button(((WIDTH/2) - 170, (HEIGHT/4) + 70, 320, 30), 'Rapidly Airdrop Food to Selected Country', lambda: apply_action("Rapidly Airdrop Food to Selected Country"))
faobutton2 = Button(((WIDTH/2) - 140, (HEIGHT/4) + 170, 250, 30), 'Ship Food to Selected Country', lambda: apply_action("Ship Food to Selected Country"))
faobutton3 = Button(((WIDTH/2) - 155, (HEIGHT/4) + 270, 290, 30), "Distribute Food to Countries in Need", lambda: apply_action("Distribute Food to Countries in Need"))

faobutton1.callback = lambda: (popup_fao.hide(), apply_action("Rapidly Airdrop Food to Selected Country"))
faobutton2.callback = lambda: (popup_fao.hide(), apply_action("Ship Food to Selected Country"))
faobutton3.callback = lambda: (popup_fao.hide(), apply_action("Distribute Food to Countries in Need"))

wfpbutton1 = Button(((WIDTH/2) - 140, (HEIGHT/4) + 70, 250, 30), "Subsidize Farming", lambda: apply_action("Subsidize Farming"))
wfpbutton2 = Button(((WIDTH/2) - 200, (HEIGHT/4) + 170, 400, 30), "Cure Plant/Animal Disease in Selected Country", lambda: apply_action("Cure Plant/Animal Disease in Selected Country"))
wfpbutton3 = Button(((WIDTH/2) - 200, (HEIGHT/4) + 270, 400, 30), "Implement Global Agricultural Education Programs", lambda: apply_action("Implement Global Agricultural Education Programs"))

wfpbutton1.callback = lambda: (popup_wfp.hide(), apply_action("Subsidize Farming"))
wfpbutton2.callback = lambda: (popup_wfp.hide(), apply_action("Cure Plant/Animal Disease in Selected Country"))
wfpbutton3.callback = lambda: (popup_wfp.hide(), apply_action("Implement Global Agricultural Education Programs"))



budgetButton = Button((2*(WIDTH/5), HEIGHT-100, WIDTH/5, 100), f"Budget: {budget:,}", lambda: None)
popup_budget = Popup(popup_rect, "Budget", "Budget is currently stable.", font_small)
budgetButton.callback = lambda pop=popup_budget: pop.show(title=pop.title, text=pop.text, buttons=pop.buttons)

# --- Game loop ---




running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # delta seconds

    # ----------------------------------------
    #             INPUT HANDLING
    # ----------------------------------------



    # compute average world health (clamp 0..100) and update profit_rate accordingly
    
    for i in range(58):
        if(country_health[i]>100):
            country_health[i]=100
            
    average_health = sum(country_health)/ len(country_health)
    average_famine= 70 - (sum(country_famine)/len(country_famine))
    total_average_hp=average_health + average_famine

    # profit scales linearly: 0% -> 0, 100% -> MAX_PROFIT
    profit_rate = int((average_health / 100.0) * MAX_PROFIT)

    # apply profit per whole second using accumulator (handles fractional dt)
    budget_acc += dt
    if budget_acc >= 1.0:
        secs = int(budget_acc)
        budget += profit_rate * secs
        budget_acc -= secs

    # update popup/button labels to reflect latest values
    popup_budget.title = f"Budget: ${budget:,}"
    popup_budget.text = f"Profit rate: ${profit_rate:,}/s"
    budgetButton.text = f"Budget: ${budget:,}"
    
    



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # If any popup is active, route events to it and skip other UI handling
        active_popup = None
        for p in (popup_budget, popup_wfp, popup_fao, popup_country):
            if p.active:
                active_popup = p
                break
        if active_popup:
            active_popup.handle_event(event)
            continue
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos    
            if event.button == 1:
                mx = max(0, min(WIDTH - 1, mouse_x))
                my = max(0, min(HEIGHT - 1, mouse_y))
                
                # single lookup on id_map instead of looping masks
                col = id_map.get_at((mx, my))
                idx = col.r - 1  # we encoded index+1 in red channel
                if 0 <= idx <= MAX_ICONS:
                    name = country_names.get(idx, f"Unknown ({idx})")
                    
                
                        
         
                    if pending_action:
                        # Apply the action to the selected country
                        budget=apply_action_to_country(pending_action, idx,budget)
                        pending_action = None  # Reset pending action
                        print(f"Applied '{pending_action}' to {name}")
                    else:
                    #INPUT HEALTH VALUE AND FAMINE STATUS
                        health_val = country_health[idx]+country_famine[idx]
                        famine = "Yes" if idx in infected_countries else "No"
                        body = f"Health: {health_val}\nFamine?: {famine}"
                    # position popup slightly offset from click so cursor doesn't cover it
                        popup_country.show(title=name, text=body, buttons=popup_country.buttons, pos=(mx + 12, my + 12))
                #INPUT HEALTH VALUE AND FAMINE STATUS ABOVE

            
        wfpButton.handle_event(event)
        faoButton.handle_event(event)
        budgetButton.handle_event(event)
        

    
    # ----------------------------------------
    #              GAME LOGIC
    # ----------------------------------------
    news_ticker.update(dt)

    # infect
    if not game_won and random.randint(0, 900)==1:
        neighbors=countries_neighbors.get(random.choice(infected_countries))
        new_infected=random.choice(neighbors)
        if new_infected not in infected_countries:
            infected_countries.append(new_infected)
            news.append(f'Famine detected in {country_names[new_infected]}! ')
            news_ticker.refresh()
    elif not game_won and random.randint(0, 5000)==1:
        new_infected=random.randint(0, 58)
        if new_infected not in infected_countries:
            infected_countries.append(new_infected)
            disease=random.choice(agriculture_diseases + animal_diseases)
            news.append(f'Disease {disease} has caused famine in {country_names[new_infected]}!')
            news_ticker.refresh()

    #update health
    for i in range(58):
        if random.randint(0, 50)==1:
            country_famine[i]= max(0, country_famine[i]-1) if i in infected_countries else min(70, country_famine[i]+1)
        if i in infected_countries and random.randint(0, 100)==1:
            country_health[i]= max(0, country_health[i]-1)


    if average_health==30 and average_famine==70:
        news=['Congradulations! You have stopped the famine crisis. You win!']
    
        
    

    # ----------------------------------------
    #               DRAWING
    # ----------------------------------------

    healthBox = InfoBox((3*(WIDTH/5), HEIGHT-100, WIDTH/5, 100), f"Health: {int((100*average_health)/30)}", bg=(200,200,200))
    hungerBox = InfoBox((4*(WIDTH/5), HEIGHT-100, WIDTH/5, 100), f"Hunger: {int((100*average_famine)/70)}", bg=(200,200,200))

    # Draw background
    screen.blit(background, (0, 0))
    screen.blit(newsImg, (WIDTH/4 - ticker_height, 0))

    for idx, overlay in enumerate(map_overlays):
        health_val = country_health[idx] + country_famine[idx] if idx < len(country_health) else 100
        # linear mapping: health 100 -> 0 alpha, health 0 -> 255 alpha
        alpha = int((100.0 - health_val) / 100.0 * 255.0)
        alpha = max(0, min(255, alpha))
        if alpha == 0:
            # skip blitting entirely when fully clear
            continue
        tmp = overlay.copy()
        tmp.set_alpha(alpha)
        screen.blit(tmp, (0, 0))

    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_x = max(0, min(WIDTH - 1, mouse_x))
    mouse_y = max(0, min(HEIGHT - 1, mouse_y))

    col = id_map.get_at((mouse_x, mouse_y))
    hover_idx = col.r - 1
    if 0 <= hover_idx <= MAX_ICONS and hover_idx < len(map_masks):
        # use the precomputed highlight surface
        screen.blit(hover_highlights[hover_idx], (0, 0))
        
        
    wfpButton.draw(screen, font_small)
    faoButton.draw(screen, font_small)
    budgetButton.draw(screen, font_small)
    healthBox.draw(screen, font_small)
    hungerBox.draw(screen, font_small)    
    
    

    news_ticker.draw(screen)
    
    for p in (popup_budget, popup_wfp, popup_fao, popup_country):
        p.draw(screen)


    # Draw menus
    # if menu is open, draw
    
   

    # Update display
    pygame.display.flip()

pygame.quit()