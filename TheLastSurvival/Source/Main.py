import pygame
import os
import random
import csv
import json
from Config import *
from Screen import *
from Var import *
from InitAssets import *
from Obts import *
from Util import load_save, reset_keys
from Control import Controls_Handler

pygame.init()

class Soldier(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
		pygame.sprite.Sprite.__init__(self)
		self.char_type = char_type
		if char_type == 'player':
			self.health = 100
		if char_type == 'player2':
			self.health = 50
		else:
			self.health = 100
		self.alive = True
		self.speed = speed
		self.ammo = ammo
		self.start_ammo = ammo
		self.shoot_cooldown = 0
		self.grenades = grenades
		self.max_health = self.health
		self.direction = 1
		self.vel_y = 0
		self.jump = False
		self.in_air = True
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()
		#ai specific variables
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20)
		self.idling = False
		self.idling_counter = 0
		
		#load all images for the players
		animation_types = ['Idle', 'Run', 'Jump', 'Death']
		for animation in animation_types:
			#reset temporary list of images
			temp_list = []
			#count number of files in the folder
			num_of_frames = len(os.listdir(f'Assets/Image/{self.char_type}/{animation}'))
			for i in range(num_of_frames):
				img = pygame.image.load(f'Assets/Image/{self.char_type}/{animation}/{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)

		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()


	def update(self):
		self.update_animation()
		self.check_alive()
		#update cooldown
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1


	def move(self, moving_left, moving_right):
		#reset movement variables
		screen_scroll = 0
		dx = 0
		dy = 0

		#assign movement variables if moving left or right
		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1

		#jump
		if self.jump == True and self.in_air == False:
			self.vel_y = -11
			self.jump = False
			self.in_air = True

		#apply gravity
		self.vel_y += GRAVITY
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y

		#check for collision
		for tile in world.obstacle_list:
			#check collision in the x direction
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
				#if the ai has hit a wall then make it turn around
				if self.char_type == 'enemy':
					self.direction *= -1
					self.move_counter = 0
			#check for collision in the y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				#check if below the ground, i.e. jumping
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				#check if above the ground, i.e. falling
				elif self.vel_y >= 0:
					self.vel_y = 0
					self.in_air = False
					dy = tile[1].top - self.rect.bottom

		#check for collision with water
		if pygame.sprite.spritecollide(self, InitAssets.SpriteGr.water_group, False):
			self.health = 0

		#check for collision with exit
		level_complete = False
		if pygame.sprite.spritecollide(self, InitAssets.SpriteGr.exit_group, False):
			level_complete = True

		#check if fallen off the map
		if self.rect.bottom > Screen.Resolution.SCREEN_HEIGHT:
			self.health = 0


		#check if going off the edges of the screen
		if self.char_type == 'player' or 'player2':
			if self.rect.left + dx < 0 or self.rect.right + dx > Screen.Resolution.SCREEN_WIDTH:
				dx = 0

		#update rectangle position
		self.rect.x += dx
		self.rect.y += dy

		#update scroll based on player position
		if self.char_type == 'player' or 'player2':
			if (self.rect.right > Screen.Resolution.SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - Screen.Resolution.SCREEN_WIDTH)\
				or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
				self.rect.x -= dx
				screen_scroll = -dx

		return screen_scroll, level_complete

	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			InitAssets.SpriteGr.bullet_group.add(bullet)
			#reduce ammo
			self.ammo -= 1


	def ai(self):
		if self.alive and player.alive:
			if self.idling == False and random.randint(1, 200) == 1:
				self.update_action(0)#0: idle
				self.idling = True
				self.idling_counter = 50
			#check if the ai in near the player
			if self.vision.colliderect(player.rect):
				#stop running and face the player
				self.update_action(0)#0: idle
				#shoot
				self.shoot()
			else:
				if self.idling == False:
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left, ai_moving_right)
					self.update_action(1)#1: run
					self.move_counter += 1
					#update ai vision as the enemy moves
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

					if self.move_counter > TILE_SIZE:
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False
		#scroll
		self.rect.x += screen_scroll

	def update_animation(self):
		#update animation
		ANIMATION_COOLDOWN = 100
		#update image depending on current frame
		self.image = self.animation_list[self.action][self.frame_index]
		#check if enough time has passed since the last update
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		#if the animation has run out the reset back to the start
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:
				self.frame_index = 0



	def update_action(self, new_action):
		#check if the new action is different to the previous one
		if new_action != self.action:
			self.action = new_action
			#update the animation settings
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()



	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)


	def draw(self):
		Screen.Resolution.screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

#init World
class World():
	def __init__(self):
		self.obstacle_list = []

	def process_data(self, data):
		self.level_length = len(data[0])
		#iterate through each value in level data file
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = InitAssets.Tiles.img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * TILE_SIZE
					img_rect.y = y * TILE_SIZE
					tile_data = (img, img_rect)
					if tile >= 0 and tile <= 8:
						self.obstacle_list.append(tile_data)
					elif tile >= 9 and tile <= 10:
						water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
						InitAssets.SpriteGr.water_group.add(water)
					elif tile >= 11 and tile <= 14:
						decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
						InitAssets.SpriteGr.decoration_group.add(decoration)
					elif tile == 15 and Var.character == 1:#create player
						player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
						health_bar = Screen.HealthBar(10, 10, player.health, player.health)
					elif tile == 16 and Var.character == 2:#create player2
						player = Soldier('player2', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
						health_bar = Screen.HealthBar(10, 10, player.health, player.health)
					elif tile == 17:#create enemies
						enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0)
						InitAssets.SpriteGr.enemy_group.add(enemy)
					elif tile == 18:#create ammo box
						item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
						InitAssets.SpriteGr.item_box_group.add(item_box)
					elif tile == 19:#create grenade box
						item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
						InitAssets.SpriteGr.item_box_group.add(item_box)
					elif tile == 20:#create health box
						item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
						InitAssets.SpriteGr.item_box_group.add(item_box)
					elif tile == 21:#create exit
						exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
						InitAssets.SpriteGr.exit_group.add(exit)

		return player, health_bar


	def draw(self):
		for tile in self.obstacle_list:
			tile[1][0] += screen_scroll
			Screen.Resolution.screen.blit(tile[0], tile[1])


class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = InitAssets.Items.item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


	def update(self):
		#scroll
		self.rect.x += screen_scroll
		#check if the player has picked up the box
		if pygame.sprite.collide_rect(self, player):
			#check what kind of box it was
			if self.item_type == 'Health':
				player.health += 25
				if player.health > player.max_health:
					player.health = player.max_health
			elif self.item_type == 'Ammo':
				player.ammo += 15
			elif self.item_type == 'Grenade':
				player.grenades += 3
			#delete the item box
			self.kill()

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = InitAssets.Bullet.bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		#move bullet
		self.rect.x += (self.direction * self.speed)
		#check if bullet has gone off screen
		if self.rect.right < 0 or self.rect.left > Screen.Resolution.SCREEN_WIDTH:
			self.kill()
		#check for collision with level
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()

		#check collision with characters
		if pygame.sprite.spritecollide(player, InitAssets.SpriteGr.bullet_group, False):
			if player.alive:
				player.health -= 5
				self.kill()
		for enemy in InitAssets.SpriteGr.enemy_group:
			if pygame.sprite.spritecollide(enemy, InitAssets.SpriteGr.bullet_group, False):
				if enemy.alive:
					enemy.health -= 25
					Var.score += 10
					self.kill()

class Grenade(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.timer = 100
		self.vel_y = -11
		self.speed = 7
		self.image = InitAssets.Grenade.grenade_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.direction = direction

	def update(self):
		self.vel_y += GRAVITY
		dx = self.direction * self.speed
		dy = self.vel_y

		#check for collision with level
		for tile in world.obstacle_list:
			#check collision with walls
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				self.direction *= -1
				dx = self.direction * self.speed
			#check for collision in the y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				self.speed = 0
				#check if below the ground, i.e. thrown up
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				#check if above the ground, i.e. falling
				elif self.vel_y >= 0:
					self.vel_y = 0
					dy = tile[1].top - self.rect.bottom	


		#update grenade position
		self.rect.x += dx + screen_scroll
		self.rect.y += dy

		#countdown timer
		self.timer -= 1
		if self.timer <= 0:
			self.kill()
			explosion = Explosion(self.rect.x, self.rect.y, 0.5)
			InitAssets.SpriteGr.explosion_group.add(explosion)
			#do damage to anyone that is nearby
			if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
				abs(self.rect.centery - player.rect.centery) <  TILE_SIZE * 2:
				player.health -= 50
			for enemy in InitAssets.SpriteGr.enemy_group:
				if abs(self.rect.centerx - enemy.rect.centerx) <  TILE_SIZE * 2 and \
					abs(self.rect.centery - enemy.rect.centery) <  TILE_SIZE * 2:
					enemy.health -= 50

class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
	#scroll
	def update(self):
		self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
	#scroll
	def update(self):
		self.rect.x += screen_scroll

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

class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	#scroll
	def update(self):
		self.rect.x += screen_scroll

#define font
class Font():
	def syncFont():
		font = pygame.font.SysFont('Futura', 30)

	def draw_text(text, font, text_col, x, y):
		img = pygame.font.SysFont('Futura', 30).render(text, True, text_col)
		Screen.Resolution.screen.blit(img, (x, y))

def show_score(a, b):
    score_point = score_font.render("Score : " + str(Var.score), True, (255, 255, 255))
    Screen.Resolution.screen.blit(score_point, (a, b))

def show_score_dead(a, b):
    score_point = score_font.render("Your Score : " + str(Var.score), True, (255, 255, 255))
    Screen.Resolution.screen.blit(score_point, (a, b))

def draw_bg(a):
	Screen.Resolution.screen.fill(Screen.Colours.BG)
	if a == 1:
		width = Screen.Background.forest_img.get_width()
		for x in range(1): 
			Screen.Resolution.screen.blit(Screen.Background.forest_img, ((x * width) - Var.bg_scroll * 0.7, Screen.Resolution.SCREEN_HEIGHT - Screen.Background.forest_img.get_height()))
	if a == 2:
		width = Screen.Background.beach_img.get_width()
		for x in range(1): 
			Screen.Resolution.screen.blit(Screen.Background.beach_img, ((x * width) - Var.bg_scroll * 0.7, Screen.Resolution.SCREEN_HEIGHT - Screen.Background.beach_img.get_height()))

with open('save.json','r') as data:
	base = json.load(data)
	if base['current_profile'] == 0:
		if base['controls']['0']['Character'] == 49:
			Var.character = 1
		if base['controls']['0']['Character'] == 50:
			Var.character = 2
		if base['controls']['0']['Environment'] == 1073741913:
			Var.game_environment = 1
		if base['controls']['0']['Environment'] == 1073741914:
			Var.game_environment = 2
	if base['current_profile'] == 1:
		if base['controls']['1']['Character'] == 49:
			Var.character = 1
		if base['controls']['1']['Character'] == 50:
			Var.character = 2
		if base['controls']['1']['Environment'] == 1073741913:
			Var.game_environment = 1
		if base['controls']['1']['Environment'] == 1073741914:
			Var.game_environment = 2

#create empty tile list
world_data = []
for row in range( ROWS):
    r = [-1] *  COLS
    world_data.append(r)
#load in level data and create world
if Var.game_environment == 1:
	with open(f'Source/Forest/level{ level}_data.csv', newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		for x, row in enumerate(reader):
			for y, tile in enumerate(row):
				world_data[x][y] = int(tile)
	world = World()
	player, health_bar = world.process_data(world_data)
if Var.game_environment == 2:
	with open(f'Source/Coastal/level{ level}_data.csv', newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		for x, row in enumerate(reader):
			for y, tile in enumerate(row):
				world_data[x][y] = int(tile)
	world = World()
	player, health_bar = world.process_data(world_data)

actions = {"Left": False, "Right": False, "Jump": False, "Shoot": False, "Nade": False, "Start": False, "Action1": False, "Character": False, "Environment": False}

save = load_save()
control_handler = Controls_Handler(save)

run = True
pause = False
score_font = pygame.font.SysFont('Futura', 32)

while run:

	#set FPS
	Screen.Frame.clock.tick(Screen.Frame.FPS)
	if start_game == False and setting_menu == False:
		#draw menu
		Screen.Resolution.screen.fill(Screen.Colours.BG)
		#add buttons
		if Button.start_button.draw(Screen.Resolution.screen):
			start_game = True
			start_intro = True
			setting_menu = False
		if Button.setting_button.draw(Screen.Resolution.screen):
			start_game = False
			start_intro = False
			setting_menu = True
		if Button.exit_button.draw(Screen.Resolution.screen):
			run = False
	if setting_menu == True:
		while setting_menu:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					run = False
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_0:
						setting_menu = False
					if event.key == pygame.K_ESCAPE:
						run = False
					if event.key == control_handler.controls['Left']:
						actions['Left'] = True
					if event.key == control_handler.controls['Right']:
						actions['Right'] = True
					if event.key == control_handler.controls['Jump']:
						actions['Jump'] = True
					if event.key == control_handler.controls['Nade']:
						actions['Nade'] = True
					if event.key == control_handler.controls['Shoot']:
						actions['Shoot'] = True
					if event.key == control_handler.controls['Start']:
						actions['Start'] = True
					if event.key == control_handler.controls['Action1']:
						actions['Action1'] = True
					if event.key == control_handler.controls['Character']:
						actions['Character'] = True
					if event.key == control_handler.controls['Environment']:
						actions['Environment'] = True

				if event.type == pygame.KEYUP:
					if event.key == control_handler.controls['Left']:
						actions['Left'] = False
					if event.key == control_handler.controls['Right']:
						actions['Right'] = False
					if event.key == control_handler.controls['Jump']:
						actions['Jump'] = False
					if event.key == control_handler.controls['Nade']:
						actions['Nade'] = False
					if event.key == control_handler.controls['Shoot']:
						actions['Shoot'] = False
					if event.key == control_handler.controls['Start']:
						actions['Start'] = False
					if event.key == control_handler.controls['Action1']:
						actions['Action1'] = False
					if event.key == control_handler.controls['Character']:
						actions['Character'] = False
					if event.key == control_handler.controls['Environment']:
						actions['Environment'] = False
			canvas = pygame.Surface((Screen.Resolution.SCREEN_WIDTH, Screen.Resolution.SCREEN_HEIGHT))
			#UPDATE THE GAME
			control_handler.update(actions)
			#RENDER WINDOW AND DISPLAY
			canvas.fill((135, 206, 235))
			control_handler.render(canvas)
			Screen.Resolution.screen.blit(pygame.transform.scale(canvas, (Screen.Resolution.SCREEN_WIDTH * 2,Screen.Resolution.SCREEN_HEIGHT * 2) ), (0,0))
			pygame.display.update()
			reset_keys(actions)
	if start_game == True:
		#update background
		draw_bg(Var.game_environment)
		#draw world map
		world.draw()
		#show player health
		health_bar.draw(player.health)
		#show ammo
		Font.draw_text('AMMO: ', Font.syncFont, Screen.Colours.WHITE, 10, 35)
		for x in range(player.ammo):
			Screen.Resolution.screen.blit(InitAssets.Bullet.bullet_img, (90 + (x * 10), 40))
		#show grenades
		Font.draw_text('GRENADES: ', Font.syncFont, Screen.Colours.WHITE, 10, 60)
		for x in range(player.grenades):
			Screen.Resolution.screen.blit(InitAssets.Grenade.grenade_img, (135 + (x * 15), 60))


		player.update()
		player.draw()

		for enemy in InitAssets.SpriteGr.enemy_group:
			enemy.ai()
			enemy.update()
			enemy.draw()

		#update and draw groups
		InitAssets.SpriteGr.bullet_group.update()
		InitAssets.SpriteGr.grenade_group.update()
		InitAssets.SpriteGr.explosion_group.update()
		InitAssets.SpriteGr.item_box_group.update()
		InitAssets.SpriteGr.decoration_group.update()
		InitAssets.SpriteGr.water_group.update()
		InitAssets.SpriteGr.exit_group.update()
		InitAssets.SpriteGr.bullet_group.draw(Screen.Resolution.screen)
		InitAssets.SpriteGr.grenade_group.draw(Screen.Resolution.screen)
		InitAssets.SpriteGr.explosion_group.draw(Screen.Resolution.screen)
		InitAssets.SpriteGr.item_box_group.draw(Screen.Resolution.screen)
		InitAssets.SpriteGr.decoration_group.draw(Screen.Resolution.screen)
		InitAssets.SpriteGr.water_group.draw(Screen.Resolution.screen)
		InitAssets.SpriteGr.exit_group.draw(Screen.Resolution.screen)

		#show intro
		if start_intro == True:
			if Fade.intro_fade.fade():
				start_intro = False
				Fade.intro_fade.fade_counter = 0

		#update player actions
		if player.alive:
			#shoot bullets
			if shoot:
				player.shoot()
			#throw grenades
			elif grenade and grenade_thrown == False and player.grenades > 0:
				grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
							player.rect.top, player.direction)
				InitAssets.SpriteGr.grenade_group.add(grenade)
				#reduce grenades
				player.grenades -= 1
				grenade_thrown = True
			if player.in_air:
				player.update_action(2)#2: jump
			elif moving_left or moving_right:
				player.update_action(1)#1: run
			else:
				player.update_action(0)#0: idle
			screen_scroll, level_complete = player.move(moving_left, moving_right)
			bg_scroll -= screen_scroll
			#check if player has completed the level
			if level_complete:
				start_intro = True
				level += 1
				bg_scroll = 0
				world_data = InitAssets.Reset.reset_level()
				if level <= MAX_LEVELS:
					#load in level data and create world
					if Var.game_environment == 1:
						with open(f'Source/Forest/level{level}_data.csv', newline='') as csvfile:
							reader = csv.reader(csvfile, delimiter=',')
							for x, row in enumerate(reader):
								for y, tile in enumerate(row):
									world_data[x][y] = int(tile)
						world = World()
						player, health_bar = world.process_data(world_data)	
					if Var.game_environment ==2:
						with open(f'Source/Coastal/level{level}_data.csv', newline='') as csvfile:
							reader = csv.reader(csvfile, delimiter=',')
							for x, row in enumerate(reader):
								for y, tile in enumerate(row):
									world_data[x][y] = int(tile)
						world = World()
						player, health_bar = world.process_data(world_data)	
		else:
			screen_scroll = 0
			if Fade.death_fade.fade():
				show_score_dead(textX - 500, textY + 500)
				if Button.restart_button.draw(Screen.Resolution.screen):
					Fade.death_fade.fade_counter = 0
					start_intro = True
					bg_scroll = 0
					world_data = InitAssets.Reset.reset_level()
					#load in level data and create world
					if Var.game_environment == 1:
						with open(f'Source/Forest/level{level}_data.csv', newline='') as csvfile:
							reader = csv.reader(csvfile, delimiter=',')
							for x, row in enumerate(reader):
								for y, tile in enumerate(row):
									world_data[x][y] = int(tile)
						world = World()
						player, health_bar = world.process_data(world_data)	
					if Var.game_environment ==2:
						with open(f'Source/Coastal/level{level}_data.csv', newline='') as csvfile:
							reader = csv.reader(csvfile, delimiter=',')
							for x, row in enumerate(reader):
								for y, tile in enumerate(row):
									world_data[x][y] = int(tile)
						world = World()
						player, health_bar = world.process_data(world_data)	
	#pause
	if pause == True:
		while pause:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_p:
						pause = False

	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		#keyboard presses
		if event.type == pygame.KEYDOWN:
			if event.key == control_handler.controls['Left']:
				moving_left = True
			if event.key == control_handler.controls['Right']:
				moving_right = True
			if event.key == control_handler.controls['Shoot']:
				shoot = True
			if event.key == control_handler.controls['Nade']:
				grenade = True
			if event.key == control_handler.controls['Jump'] and player.alive:
				player.jump = True
			if event.key == pygame.K_ESCAPE:
				run = False
			if event.key == pygame.K_p:
				pause = True


		#keyboard button released
		if event.type == pygame.KEYUP:
			if event.key == control_handler.controls['Left']:
				moving_left = False
			if event.key == control_handler.controls['Right']:
				moving_right = False
			if event.key == control_handler.controls['Shoot']:
				shoot = False
			if event.key == control_handler.controls['Nade']:
				grenade = False
				grenade_thrown = False

	show_score(textX, textY)
	pygame.display.update()

pygame.quit()