import pygame
import os
import random
import csv
import Var,Screen,Config

#store tiles in a list
class Tiles():
    img_list = []
    for x in range(Var.TILE_TYPES):
        img = pygame.image.load(f'Assets/Image/Tile/{x}.png')
        img = pygame.transform.scale(img, (Var.TILE_SIZE, Var.TILE_SIZE))
        img_list.append(img)

#init effect
#create buttons
class Button():
	start_button = Config.Client(Screen.Resolution.SCREEN_WIDTH // 2 - 130, Screen.Resolution.SCREEN_HEIGHT // 2 - 150, Screen.Menu.start_img, 1)
	exit_button = Config.Client(Screen.Resolution.SCREEN_WIDTH // 2 - 110, Screen.Resolution.SCREEN_HEIGHT // 2 + 50, Screen.Menu.exit_img, 1)
	restart_button = Config.Client(Screen.Resolution.SCREEN_WIDTH // 2 - 100, Screen.Resolution.SCREEN_HEIGHT // 2 - 50, Screen.Menu.restart_img, 2)
#bullet
class Bullet():
    bullet_img = pygame.image.load('Assets/Image/Icons/bullet.png').convert_alpha()
#grenade
class Grenade():
    grenade_img = pygame.image.load('Assets/Image/Icons/grenade.png').convert_alpha()
#items
class Items():
    health_box_img = pygame.image.load('Assets/Image/Icons/health_box.png').convert_alpha()
    ammo_box_img = pygame.image.load('Assets/Image/Icons/ammo_box.png').convert_alpha()
    grenade_box_img = pygame.image.load('Assets/Image/Icons/grenade_box.png').convert_alpha()
    item_boxes = {
        'Health'	: health_box_img,
        'Ammo'		: ammo_box_img,
        'Grenade'	: grenade_box_img
    }

#define font
class Font():
	def syncFont():
		font = pygame.font.SysFont('Futura', 30)

	def draw_text(text, font, text_col, x, y):
		img = pygame.font.SysFont('Futura', 30).render(text, True, text_col)
		Screen.Resolution.screen.blit(img, (x, y))


	def draw_bg():
		Screen.Resolution.screen.fill(Screen.Colours.BG)
		width = Screen.Background.skycloud_img.get_width()
		for x in range(4):
			Screen.Resolution.screen.blit(Screen.Background.skycloud_img, ((x * width) - Var.bg_scroll * 0.5, 0))
			Screen.Resolution.screen.blit(Screen.Background.forest_img, ((x * width) - Var.bg_scroll * 0.5, 0)) 
			Screen.Resolution.screen.blit(Screen.Background.pine1_img, ((x * width) - Var.bg_scroll * 0.7, Screen.Resolution.SCREEN_HEIGHT - Screen.Background.pine1_img.get_height() - 150))

class SpriteGr():
	enemy_group = pygame.sprite.Group()
	bullet_group = pygame.sprite.Group()
	grenade_group = pygame.sprite.Group()
	explosion_group = pygame.sprite.Group()
	item_box_group = pygame.sprite.Group()
	decoration_group = pygame.sprite.Group()
	water_group = pygame.sprite.Group()
	exit_group = pygame.sprite.Group()

class Reset():
	def reset_level():
		SpriteGr.enemy_group.empty()
		SpriteGr.bullet_group.empty()
		SpriteGr.grenade_group.empty()
		SpriteGr.explosion_group.empty()
		SpriteGr.item_box_group.empty()
		SpriteGr.decoration_group.empty()
		SpriteGr.water_group.empty()
		SpriteGr.exit_group.empty()

		#create empty tile list
		data = []
		for row in range(Var.ROWS):
			r = [-1] * Var.COLS
			data.append(r)

		return data

class ScreenFade():
	def __init__(self, direction, colour, speed):
		self.direction = direction
		self.colour = colour
		self.speed = speed
		self.fade_counter = 0


	def fade(self):
		fade_complete = False
		self.fade_counter += self.speed
		if self.direction == 1:#whole screen fade
			pygame.draw.rect(Screen.Resolution.screen, self.colour, (0 - self.fade_counter, 0, Screen.Resolution.SCREEN_WIDTH // 2, Screen.Resolution.SCREEN_HEIGHT))
			pygame.draw.rect(Screen.Resolution.screen, self.colour, (Screen.Resolution.SCREEN_WIDTH // 2 + self.fade_counter, 0, Screen.Resolution.SCREEN_WIDTH, Screen.Resolution.SCREEN_HEIGHT))
			pygame.draw.rect(Screen.Resolution.screen, self.colour, (0, 0 - self.fade_counter, Screen.Resolution.SCREEN_WIDTH, Screen.Resolution.SCREEN_HEIGHT // 2))
			pygame.draw.rect(Screen.Resolution.screen, self.colour, (0, Screen.Resolution.SCREEN_HEIGHT // 2 +self.fade_counter, Screen.Resolution.SCREEN_WIDTH, Screen.Resolution.SCREEN_HEIGHT))
		if self.direction == 2:#vertical screen fade down
			pygame.draw.rect(Screen.Resolution.screen, self.colour, (0, 0, Screen.Resolution.SCREEN_WIDTH, 0 + self.fade_counter))
		if self.fade_counter >= Screen.Resolution.SCREEN_WIDTH:
			fade_complete = True

		return fade_complete

#create screen fades
class Fade():
	intro_fade = ScreenFade(1, Screen.Colours.BLACK, 4)
	death_fade = ScreenFade(2, Screen.Colours.PINK, 4)

