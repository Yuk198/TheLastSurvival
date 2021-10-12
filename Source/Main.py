import pygame
import os
import random
import csv
from Screen import *
from Var import *
from InitAssets import *
from Obts import *
from Element import *

pygame.init()

run = True
while run:

	#set FPS
	Screen.Frame.clock.tick(Screen.Frame.FPS)

	#update background
	InitAssets.Font.draw_bg()
	#draw world map
	world.draw()
	#show player health
	health_bar.draw(player.health)
	#show ammo
	InitAssets.Font.draw_text('AMMO: ', InitAssets.Font.syncFont, Screen.Colours.WHITE, 10, 35)
	for x in range(player.ammo):
		Screen.Resolution.screen.blit(InitAssets.Bullet.bullet_img, (90 + (x * 10), 40))
	#show grenades
	InitAssets.Font.draw_text('GRENADES: ', InitAssets.Font.syncFont, Screen.Colours.WHITE, 10, 60)
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


	#update player actions
	if player.alive:
		#shoot bullets
		if Var.PlayerVar.shoot:
			player.shoot()
		#throw grenades
		elif Var.PlayerVar.grenade and Var.PlayerVar.grenade_thrown == False and player.grenades > 0:
			grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
			 			player.rect.top, player.direction)
			InitAssets.SpriteGr.grenade_group.add(grenade)
			#reduce grenades
			player.grenades -= 1
			Var.PlayerVar.grenade_thrown = True
		if player.in_air:
			player.update_action(2)#2: jump
		elif Var.PlayerVar.moving_left or Var.PlayerVar.moving_right:
			player.update_action(1)#1: run
		else:
			player.update_action(0)#0: idle
		player.move(Var.PlayerVar.moving_left, Var.PlayerVar.moving_right)


	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		#keyboard presses
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				Var.PlayerVar.moving_left = True
			if event.key == pygame.K_d:
				Var.PlayerVar.moving_right = True
			if event.key == pygame.K_SPACE:
				Var.PlayerVar.shoot = True
			if event.key == pygame.K_q:
				Var.PlayerVar.grenade = True
			if event.key == pygame.K_w and player.alive:
				player.jump = True
			if event.key == pygame.K_ESCAPE:
				run = False


		#keyboard button released
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				Var.PlayerVar.moving_left = False
			if event.key == pygame.K_d:
				Var.PlayerVar.moving_right = False
			if event.key == pygame.K_SPACE:
				Var.PlayerVar.shoot = False
			if event.key == pygame.K_q:
				Var.PlayerVar.grenade = False
				Var.PlayerVar.grenade_thrown = False


	pygame.display.update()

pygame.quit()