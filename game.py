import pygame
import pygame_menu
import webbrowser
from my_theme import mytheme
from pygame_menu.themes import Theme
from time import sleep

class Game:
    def __init__(self):
        pygame.init()
        self.running, self.playing = True, False
        self.DISPLAY_W, self.DISPLAY_H = 1200, 800
        self.display = pygame.Surface((self.DISPLAY_W, self.DISPLAY_H))
        self.window = pygame.display.set_mode((self.DISPLAY_W, self.DISPLAY_H))
        self.rulebookOpen = False
        font = pygame.font.Font('Munro-2LYe.ttf', 36)
        self.link_rect = None
        self.link_url = None
        self.rulebook = None
        self.rulebookScreen = None
        self.mainmenu = None
        self.close_rect = None
        self.difficulty = 1
        self.playmenu = None
        # create a text surface object,
        # on which text is drawn on it.
        self.text1 = font.render('Log In To See', True, (255, 255, 255))
        self.text2 = font.render('Where You Place On The', True, (255, 255, 255))
        self.text3 = font.render('Leaderboard!', True, (255, 255, 255))

        self.r_text1 = pygame.transform.rotate(self.text1, -35)
        self.r_text2 = pygame.transform.rotate(self.text2, -35)
        self.r_text3 = pygame.transform.rotate(self.text3, -35)

        # create a rectangular object for the
        # text surface object
        self.textRect1 = self.r_text1.get_rect()
        self.textRect2 = self.r_text2.get_rect()
        self.textRect3 = self.r_text3.get_rect()
        # setting position of the text
        self.textRect1.center = (1900 // 2, 500 // 2)
        self.textRect2.center = (1860 // 2, 550 // 2)
        self.textRect3.center = (1820 // 2, 600 // 2)

        # Load and scale images for background
        self.bg_img1 = pygame.image.load('ship1.png')
        self.bg_img1 = pygame.transform.scale(self.bg_img1, (500, 500))
        self.bg_img3 = pygame.image.load('ship3.png')
        self.bg_img3 = pygame.transform.scale(self.bg_img3, (600, 600))

        self.create_playmenu()
        self.create_mainmenu()

    def create_mainmenu(self):
        self.mainmenu = pygame_menu.Menu('BattleShip', 1200, 800, theme=mytheme)
        self.mainmenu.add.button('Play', self.start_the_game)
        self.mainmenu.add.button('Rules', self.open_rulebook)
        self.mainmenu.add.button('Quit', self.send_quit_event)

    def start_the_game(self):
        self.playing = True


        print("playing")

    def open_rulebook(self):
        self.rulebookOpen = True

        self.rulebook = pygame.Surface((self.DISPLAY_W, self.DISPLAY_H), pygame.SRCALPHA)
        self.rulebook.fill((0, 0, 0, 200))
        self.window.blit(self.rulebook, (0, 0))

        self.rulebookScreen = pygame.Surface((600, 450))
        self.rulebookScreen.fill((84, 150, 255))

        close_font = pygame.font.Font('Munro-2LYe.ttf', 40)
        close_text = "X"
        close_color = (255, 255, 255)
        close_bg_color = (200, 0, 0)

        close_surface = close_font.render(close_text, True, close_color)
        close_button = pygame.Surface((45, 45))
        close_button.fill(close_bg_color)

        close_text_rect = close_surface.get_rect(center=(25, 20))
        close_button.blit(close_surface, close_text_rect)

        self.close_rect = close_button.get_rect()
        self.close_rect.topleft = (300 + 600 - 45, 200)

        rulebook_font = pygame.font.Font('Munro-2LYe.ttf', 31)
        rulebook_text = ("Welcome to BattleShip!\n"
                         "Game Rules:\n1. Place your ships on the grid.\n"
                         "2. Take turns firing at a square\n on the opponent's grid.\n"
                         "3. If you hit a ship, that square is marked\n and you get another turn.\n"
                         "3. Hit all parts of ship to sink it.\n"
                         "4. First to sink all enemy ships wins!\n"
                         "Enjoy the game!")

        link_text = "Click for official instructions"
        link_color = (255, 255, 0)
        self.link_url = "https://www.hasbro.com/common/instruct/battleship.pdf"

        link_surface = rulebook_font.render(link_text, True, link_color)
        self.link_rect = link_surface.get_rect()
        self.link_rect.center = (self.DISPLAY_W // 2, 600)

        lines = rulebook_text.split('\n')
        rendered_lines = []
        y_offset = 230  # Starting Y position for the first line
        line_height = rulebook_font.get_linesize()  # Get the recommended line height for the font

        for i, line in enumerate(lines):
            if line.strip():
                rulebook_text_surface = rulebook_font.render(line, True, (255, 255, 255))
                rulebook_text_rect = rulebook_text_surface.get_rect()
                rulebook_text_rect.center = (self.DISPLAY_W // 2, y_offset + i * line_height)
                rendered_lines.append((rulebook_text_surface, rulebook_text_rect))

        while self.rulebookOpen:
            self.window.blit(self.rulebookScreen, (300, 200))
            self.window.blit(link_surface, self.link_rect)
            self.window.blit(close_button, self.close_rect)
            for rulebook_text_surface, rulebook_text_rect in rendered_lines:
                self.window.blit(rulebook_text_surface, rulebook_text_rect)

            self.check_events()
            pygame.display.flip()

    def send_quit_event(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def change_difficulty(self, value, difficulty):
        self.difficulty = difficulty

    def close_playmenu(self):
        self.playing = False

    def create_playmenu(self):
        self.playmenu = pygame_menu.Menu('BattleShip', 1200, 800, theme=mytheme)
        self.playmenu.add.button('Start Game', self.start_the_game)
        self.playmenu.add.selector('Difficulty', [('Easy', 1), ('Medium', 2), ('Hard', 3)], onchange=self.change_difficulty)
        self.playmenu.add.button('Back', self.close_playmenu)


    def draw_main_background(self):
        self.window.fill((84, 150, 255))
        self.window.blit(self.bg_img1, (700, 300))
        self.window.blit(self.bg_img3, (0, 200))
        self.window.blit(self.r_text1, self.textRect1)
        self.window.blit(self.r_text2, self.textRect2)
        self.window.blit(self.r_text3, self.textRect3)

    def draw_play_background(self):
        self.window.fill((84, 150, 255))
        self.window.blit(self.bg_img1, (700, 300))
        self.window.blit(self.bg_img3, (0, 200))

    def game_loop(self):
        while self.running:

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            if not self.playing:
                self.draw_main_background()
                self.mainmenu.update(events)
                self.mainmenu.draw(self.window)
            else:
                self.draw_play_background()
                self.playmenu.update(events)
                self.playmenu.draw(self.window)

            pygame.display.update()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running, self.playing, self.rulebookOpen = False, False, False
            elif event.type == pygame.KEYDOWN and self.rulebookOpen:
                if event.key == pygame.K_ESCAPE:
                    self.rulebookOpen = False
            elif event.type == pygame.MOUSEBUTTONDOWN and self.rulebookOpen:
                if self.link_rect and self.link_rect.collidepoint(event.pos):
                    webbrowser.open(self.link_url)
                elif hasattr(self, 'close_rect') and self.close_rect.collidepoint(event.pos):
                    self.rulebookOpen = False
