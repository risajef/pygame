import pygame
import time
import random

pygame.init()
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
green = (0,127,0)
blue = (0,0,127)

display_width = 800
display_height = 600
gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('Slither')

clock = pygame.time.Clock()

block_size = 10
FPS = 15

font = pygame.font.SysFont(None, 25)


def message_to_screen(msg,color):
    screen_text = font.render(msg, True, color)
    gameDisplay.blit(screen_text, [display_width/3, display_height/3])

class Snake:
    def __init__(self, name = "player 1", x = 0, y = 0, color = (0,0,0), keys = (pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT)):
        self.name = name
        self.x = round(x/float(block_size))*block_size
        self.dx = 0
        self.y = round(y/float(block_size))*block_size
        self.dy = 0
        self.list = [(x,y)]
        self.length = 1
        self.color = color
        self.up = keys[0]
        self.right = keys[1]
        self.down = keys[2]
        self.left = keys[3]
    def draw(self):
        for elem in self.list:
            gameDisplay.fill(self.color, rect = [elem[0], elem[1], block_size, block_size])

    
    

def gameLoop():
    gameExit = False
    gameOver = (False, None)
    
    player1 = Snake(
        name =  "green",
        x =     display_width / 3,
        y =     display_height / 2, 
        color = green, 
        keys =  (pygame.K_w, pygame.K_d, pygame.K_s, pygame.K_a))
    player2 = Snake(
        name =  "blue",
        x =     2 * display_width / 3, 
        y =     display_height / 2, 
        color = blue, 
        keys =  (pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT))
    players = [player1, player2]
    
    
    randAppleX = round(random.randrange(0, display_width - block_size)/float(block_size))*block_size
    randAppleY = round(random.randrange(0, display_height - block_size)/float(block_size))*block_size
    
    while not gameExit:
        while gameOver[0]:
            gameDisplay.fill(white)
            message_to_screen(gameOver[1] + " crashed, press C to play again or Q to quit", red)
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        gameExit = True
                        gameOver = False
                    if event.key == pygame.K_c:
                        gameLoop()
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameExit = True
            if event.type == pygame.KEYDOWN:
                for p in players:
                    if event.key == p.up and p.dy != block_size:
                        p.dy = -block_size
                        p.dx = 0
                    elif event.key == p.right and p.dx != -block_size:
                        p.dx = block_size
                        p.dy = 0
                    elif event.key == p.down and p.dy != -block_size:
                        p.dy = block_size
                        p.dx = 0
                    elif event.key == p.left and p.dx != block_size:
                        p.dx = -block_size
                        p.dy = 0
        
        
        # display Background
        gameDisplay.fill(white)
        
        for p in players:
            if p.x >= display_width or p.x < 0 or p.y >= display_height or p.y < 0:
                gameOver = (True, p.name)
            for pl in [pl for pl in players if pl != p]:
                if p.list[-1] in pl.list:
                    gameOver = (True, p.name)
            if p.list[-1] in p.list[:-1]:
                gameOver = (True, p.name)
            p.x += p.dx
            p.y += p.dy
            p.draw()
            p.list.append((p.x, p.y))
            if p.x == randAppleX and p.y == randAppleY:
                randAppleX = round(random.randrange(0, display_width - block_size)/float(block_size))*block_size
                randAppleY = round(random.randrange(0, display_height - block_size)/float(block_size))*block_size
                p.length += 1
            if len(p.list) > p.length:
                del p.list[0]
        
        # display Apple
        gameDisplay.fill(red, rect = [randAppleX, randAppleY, block_size, block_size])
        
        pygame.display.update()
        
        clock.tick(FPS)


    pygame.quit()
    quit()

gameLoop()

