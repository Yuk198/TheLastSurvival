import pygame
import os
import random
import Screen

#define game variables
GRAVITY = 0.4
SCROLL_THRESH = 300
ROWS = 16
COLS = 150
TILE_SIZE = Screen.Resolution.SCREEN_HEIGHT // ROWS
TILE_TYPES = 22
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False
setting_menu = False
character = 1
game_environment = 1
score = 0
textX = Screen.Resolution.SCREEN_WIDTH - 200
textY = 10

#define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False