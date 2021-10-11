import pygame, sys
from pygame.locals import *
pygame.init()
FPS = 60
fpsClock = pygame.time.Clock()

WINDOWWIDTH = 1280
WINDOWHEIGHT = 720

screen = pygame.image.load(r'C:\Users\Vu Ngoc Anh\Pictures\Screenshots\background.jfif')
screen2 = pygame.image.load(r'C:\Users\Vu Ngoc Anh\Pictures\Screenshots\bg2.png')
#screeny = 7
FL = pygame.image.load(r'C:\Users\Vu Ngoc Anh\Pictures\Screenshots\char.png')
#fl1X = 0
#fl1y = 530
screen = pygame.transform.scale(screen, (2000, 720))
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('The Last Survival')
#icon
crate1_img = pygame.image.load(r'C:\Users\Vu Ngoc Anh\Pictures\Screenshots\crate.png')
crate1x = 200
crate1y = 500
crate2_img = pygame.image.load(r'C:\Users\Vu Ngoc Anh\Pictures\Screenshots\crate.png')
crate2x = 330
crate2y = 500
crate3_img = pygame.image.load(r'C:\Users\Vu Ngoc Anh\Pictures\Screenshots\crate.png')
crate3x = 272
crate3y = 371
crate4_img = pygame.image.load(r'C:\Users\Vu Ngoc Anh\Pictures\Screenshots\crate.png')
crate4x = 1000
crate4y = 500
crate5_img = pygame.image.load(r'C:\Users\Vu Ngoc Anh\Pictures\Screenshots\crate.png')
crate5x = 1125
crate5y = 500
crate6_img = pygame.image.load(r'C:\Users\Vu Ngoc Anh\Pictures\Screenshots\crate.png')
crate6x = 1180
crate6y = 375
crate7_img = pygame.image.load(r'C:\Users\Vu Ngoc Anh\Pictures\Screenshots\crate.png')
crate7x = 1700
crate7y = 500
class Background():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.img = screen
        self.width = self.img.get_width()
        self.height = self.img.get_height()

        
    def draw(self):
        DISPLAYSURF.blit(self.img, (int(self.x), int(self.y)))
        screen.blit(crate1_img,(crate1x,crate1y))
        screen.blit(crate2_img,(crate2x,crate2y))
        screen.blit(crate3_img,(crate3x,crate3y))
        screen.blit(crate4_img,(crate4x,crate4y))
        screen.blit(crate5_img,(crate5x,crate5y))
        screen.blit(crate6_img,(crate6x,crate6y))
        screen.blit(crate7_img,(crate7x,crate7y))
        
        
        
    def update(self, player):
       x_camera = player.x - (WINDOWWIDTH/2 - player.width/2)
       if x_camera < 0:
           x_camera = 0
       if x_camera + WINDOWWIDTH > self.width:
           x_camera = self.width - WINDOWWIDTH
           self.x = -x_camera 
class Player():
    def __init__(self):
        self.width = 50
        self.height = 40
        self.x = 0
        self.y = 530
        self.img = FL
        self.jump = False
        self.surface = pygame.Surface((self.width, self.height))
        self.speed = 5

    def draw(self, bg):
        DISPLAYSURF.blit(self.img, (int(self.x + bg.x), int(self.y + bg.y)))

    def update(self, bg, left, right):
        if left == True:
            self.x -= self.speed
        if right == True:
            self.x += self.speed
        if self.x < 0:
            self.x = 0
        if self.x + self.width > bg.width:
            self.x = bg.width - self.width

def main():
    bg = Background()
    player = Player()
    left = False
    right = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    left = True
                if event.key == pygame.K_d:
                    right = True
                if event.key == pygame.K_SPACE: 
                        player.jump = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    left = False
                if event.key == pygame.K_d:
                    right = False
                if event.key == pygame.K_SPACE:
                    jump = False
        bg.draw()
        player.draw(bg)
        player.update(bg, left, right)
        bg.update(player)
        pygame.display.update()
        fpsClock.tick(FPS)

if __name__ == '__main__':
    main()
