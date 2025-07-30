import pygame
import pygame_menu
from pygame_menu import themes
from pygame_menu.themes import Theme

mytheme = Theme(background_color=(84, 150, 255, 0),
                title_background_color=(4, 47, 126, 0),
                title_font_shadow=False,
                widget_padding=10,
                widget_font_size=30,
                widget_font=pygame_menu.font.FONT_MUNRO,
                widget_font_color=(255, 255, 255),
                title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE,
                title_font=pygame_menu.font.FONT_MUNRO,
                title_font_color=(255, 255, 255),
                title_font_size=120,
                title_offset=(400, 40),
                )
