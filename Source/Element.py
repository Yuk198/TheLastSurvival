import pygame
import os
import random
import csv
import Screen,Var,InitAssets,Obts

class Soldier(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.char_type = char_type
		self.speed = speed
		self.ammo = ammo
		self.start_ammo = ammo
		self.shoot_cooldown = 0
		self.grenades = grenades
		self.health = 100
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
		dx = 0
		dy = 0

		#assign movement variables
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

		#init gravity
		self.vel_y += Var.GameVar.GRAVITY
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y

		#check for collision
		for tile in world.obstacle_list:
			#check collision in the x direction
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
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


		#update rectangle position
		self.rect.x += dx
		self.rect.y += dy


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

					if self.move_counter > Var.GameVar.TILE_SIZE:
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False

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
		#iterate through each value in level data file
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = InitAssets.Tiles.img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * Var.GameVar.TILE_SIZE
					img_rect.y = y * Var.GameVar.TILE_SIZE
					tile_data = (img, img_rect)
					if tile >= 0 and tile <= 8:
						self.obstacle_list.append(tile_data)
					elif tile >= 9 and tile <= 10:
						water = Obts.Water(img, x * Var.GameVar.TILE_SIZE, y * Var.GameVar.TILE_SIZE)
						InitAssets.SpriteGr.water_group.add(water)
					elif tile >= 11 and tile <= 14:
						decoration = Obts.Decoration(img, x * Var.GameVar.TILE_SIZE, y * Var.GameVar.TILE_SIZE)
						InitAssets.SpriteGr.decoration_group.add(decoration)
					elif tile == 15:#create player
						player = Soldier('Player', x * Var.GameVar.TILE_SIZE, y * Var.GameVar.TILE_SIZE, 1.65, 5, 20, 5)
						health_bar = Screen.HealthBar(10, 10, player.health, player.health)
					elif tile == 16:#create enemies
						enemy = Soldier('Enemy', x * Var.GameVar.TILE_SIZE, y * Var.GameVar.TILE_SIZE, 1.65, 2, 20, 0)
						InitAssets.SpriteGr.enemy_group.add(enemy)
					elif tile == 17:#create ammo box
						item_box = ItemBox('Ammo', x * Var.GameVar.TILE_SIZE, y * Var.GameVar.TILE_SIZE)
						InitAssets.SpriteGr.item_box_group.add(item_box)
					elif tile == 18:#create grenade box
						item_box = ItemBox('Grenade', x * Var.GameVar.TILE_SIZE, y * Var.GameVar.TILE_SIZE)
						InitAssets.SpriteGr.item_box_group.add(item_box)
					elif tile == 19:#create health box
						item_box = ItemBox('Health', x * Var.GameVar.TILE_SIZE, y * Var.GameVar.TILE_SIZE)
						InitAssets.SpriteGr.item_box_group.add(item_box)
					elif tile == 20:#create exit
						exit = InitAssets.Exit(img, x * Var.GameVar.TILE_SIZE, y * Var.GameVar.TILE_SIZE)
						InitAssets.SpriteGr.exit_group.add(exit)

		return player, health_bar


	def draw(self):
		for tile in self.obstacle_list:
			Screen.Resolution.screen.blit(tile[0], tile[1])


#init ItemBox
class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = InitAssets.Items.item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + Var.GameVar.TILE_SIZE // 2, y + (Var.GameVar.TILE_SIZE - self.image.get_height()))


	def update(self):
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

#init Bullet
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
					self.kill()

#init Grenade
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
		self.vel_y += Var.GameVar.GRAVITY
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
		self.rect.x += dx
		self.rect.y += dy

		#countdown timer
		self.timer -= 1
		if self.timer <= 0:
			self.kill()
			explosion = Obts.Explosion(self.rect.x, self.rect.y, 0.5)
			InitAssets.SpriteGr.explosion_group.add(explosion)
			#do damage to anyone that is nearby
			if abs(self.rect.centerx - player.rect.centerx) < Var.GameVar.TILE_SIZE * 2 and \
				abs(self.rect.centery - player.rect.centery) <  Var.GameVar.TILE_SIZE * 2:
				player.health -= 50
			for enemy in InitAssets.SpriteGr.enemy_group:
				if abs(self.rect.centerx - enemy.rect.centerx) <  Var.GameVar.TILE_SIZE * 2 and \
					abs(self.rect.centery - enemy.rect.centery) <  Var.GameVar.TILE_SIZE * 2:
					enemy.health -= 50

					
#create empty tile list
world_data = []
for row in range( Var.GameVar.ROWS):
    r = [-1] *  Var.GameVar.COLS
    world_data.append(r)
#load in level data and create world
with open(f'Source/level{ Var.GameVar.level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)
