import pygame
import os
import random
import Screen

#define game variables
class GameVar():
    GRAVITY = 0.5
    SCROLL_THRESH = 200
    ROWS = 16
    COLS = 150
    TILE_SIZE = Screen.Resolution.SCREEN_HEIGHT // ROWS
    TILE_TYPES = 21
    MAX_LEVELS = 3
    screen_scroll = 0
    bg_scroll = 0
    level = 1
    start_game = False
    start_intro = False

#define player action variables
class PlayerVar():
    moving_left = False
    moving_right = False
    shoot = False
    grenade = False
    grenade_thrown = False