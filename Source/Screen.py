import pygame
import os
import random

#set resolution
class Resolution():
	SCREEN_WIDTH = 1280
	SCREEN_HEIGHT = 720

	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	pygame.display.set_caption('The Last Survival')
    
#set frame
class Frame():
    clock = pygame.time.Clock()
    FPS = 60

#define colours
class Colours():
    BG = (144, 201, 120)
    RED = (255, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    BLACK = (0, 0, 0)
    PINK = (235, 65, 54)

#HUD
class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self, health):
		#update with new health
		self.health = health
		#calculate health ratio
		ratio = self.health / self.max_health
		pygame.draw.rect(Resolution.screen, Colours.BLACK, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(Resolution.screen, Colours.RED, (self.x, self.y, 150, 20))
		pygame.draw.rect(Resolution.screen, Colours.GREEN, (self.x, self.y, 150 * ratio, 20))

#button images
class Menu():
	start_img = pygame.image.load('Assets/Image/start_btn.png').convert_alpha()
	setting_img = pygame.image.load('Assets/Image/setting_btn.png').convert_alpha()
	exit_img = pygame.image.load('Assets/Image/exit_btn.png').convert_alpha()
	restart_img = pygame.image.load('Assets/Image/restart_btn.png').convert_alpha()

#background
class Background():
	forest_img = pygame.image.load('Assets/Image/Background/forest.png').convert_alpha()
	beach_img = pygame.image.load('Assets/Image/Background/beach.png').convert_alpha()