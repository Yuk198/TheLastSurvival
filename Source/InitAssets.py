import pygame
import os
import random
import csv
import Var,Screen

#button images
class Menu():
    start_img = pygame.image.load('Assets/Image/start_btn.png').convert_alpha()
    exit_img = pygame.image.load('Assets/Image/exit_btn.png').convert_alpha()
    restart_img = pygame.image.load('Assets/Image/restart_btn.png').convert_alpha()

#init background
class Background():
	forest_img = pygame.image.load('Assets/Image/Background/forest.png').convert_alpha()

#store tiles in a list
class Tiles():
    img_list = []
    for x in range(Var.GameVar.TILE_TYPES):
        img = pygame.image.load(f'Assets/Image/Tile/{x}.png')
        img = pygame.transform.scale(img, (Var.GameVar.TILE_SIZE, Var.GameVar.TILE_SIZE))
        img_list.append(img)

#init effect
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
        width = Background.forest_img.get_width()
        for x in range(0):
            Screen.Resolution.screen.blit(Background.forest_img, ((x * width) - Var.GameVar.bg_scroll * 0.5, 0))            

class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, scale):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 6):
			img = pygame.image.load(f'Assets/Image/Explosion/exp{num}.png').convert_alpha()
			img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
			self.images.append(img)
		self.frame_index = 0
		self.image = self.images[self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.counter = 0


	def update(self):
		EXPLOSION_SPEED = 4
		#update explosion amimation
		self.counter += 1

		if self.counter >= EXPLOSION_SPEED:
			self.counter = 0
			self.frame_index += 1
			#if the animation is complete then delete the explosion
			if self.frame_index >= len(self.images):
				self.kill()
			else:
				self.image = self.images[self.frame_index]

class SpriteGr():
	enemy_group = pygame.sprite.Group()
	bullet_group = pygame.sprite.Group()
	grenade_group = pygame.sprite.Group()
	explosion_group = pygame.sprite.Group()
	item_box_group = pygame.sprite.Group()
	decoration_group = pygame.sprite.Group()
	water_group = pygame.sprite.Group()
	exit_group = pygame.sprite.Group()

class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + Var.GameVar.TILE_SIZE // 2, y + (Var.GameVar.TILE_SIZE - self.image.get_height()))
