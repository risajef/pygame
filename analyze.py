import pygame
import time
import random
import math
import numpy as np
import copy
import pickle


pygame.init()

display_width = 1024
display_height = 768
gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('Walker')

clock = pygame.time.Clock()

block_size = 10
speed = 8
angular_speed = math.pi / 20
line_of_sight = 200 #200
sight_angle = 1

width = display_width // line_of_sight
height = display_height // line_of_sight
print(width)
print(height)


FPS = 60

font = pygame.font.SysFont(None, 25)

global cheap_distance_data_structure
cheap_distance_data_structure = np.empty([display_width // line_of_sight, display_height // line_of_sight], dtype=object)
for i in [(x, y) for x, y in np.ndindex(cheap_distance_data_structure.shape)]:
    cheap_distance_data_structure[i] = []


def near_objects(obj, struct):
    return_objects = []
    shape = np.shape(struct)
    for i in range(-1,2):
        for j in range(-1,2):
            for e in struct[(obj.index[0] + i) % width, (obj.index[1] + j) % height]:
                return_objects.append(e)
    return return_objects
  
def distance(XnY1, XnY2):
    dx = XnY1[0] - XnY2[0]
    dy = XnY1[1] - XnY2[1]
    dist = math.sqrt(dx*dx + dy*dy)
    return dist

def cheap_distance(XnY1, XnY2):
    dx = XnY1[0] - XnY2[0]
    dy = XnY1[1] - XnY2[1]
    return abs(dx) + abs(dy)
    

def drawangularline(screen, color, XnY, angle, radius):
    pygame.draw.line(screen, color, XnY, (XnY[0] + radius * math.cos(angle), XnY[1] + radius * math.sin(angle)))

def drawsector(screen, color, XnY, radius, start, end):
    points = [(XnY[0], XnY[1])]+ [(XnY[0]+radius*math.cos(angle), XnY[1]+radius*math.sin(angle)) for angle in np.linspace(start,end,5)]
    pygame.draw.polygon(screen, color, points)
    #drawangularline(screen, pygame.Color("black") , XnY, (start+end)/2, radius)

def is_in_sector(pos_player, pos_target, left, right):
    dx = pos_player[0] - pos_target[0]
    dy = pos_player[1] - pos_target[1]
    angle = (  (math.pi*2 - (math.atan2(dx,dy) ) ) - math.pi / 2) % (math.pi * 2)
    right = (right - left) % (math.pi * 2)
    angle = (angle - left) % (math.pi * 2)
    left = 0
    dist = cheap_distance(pos_player, pos_target)
    if dist < line_of_sight:
        if left <= angle <= right:
            return True
        if right < left:
            if right >= angle or angle >= left:
                return True
        elif left <= angle <= right:
            return True
    return False

def cheap_collision(circle1, circle2):
    return cheap_distance(circle1.pos, circle2.pos) < circle1.radius + circle2.radius

def collision(circle1, circle2):
    # circle from type Circle
    return distance(circle1.pos, circle2.pos) <= circle1.radius + circle2.radius

def make_message(player, message, t):
    screen_text = font.render(message, True, pygame.Color("white") )
    return (screen_text, [player.x, player.y + 5], t)

def write_message(messages):
    for message in messages:
        gameDisplay.blit(message[0], [message[1][0] , message[1][1] + 5])

class Circle:
    def __init__(self, x = 0, y = 0, radius = 1):
        self.x = x
        self.y = y
        self.pos = (x, y)
        self.radius = radius
    
    def set_x(self, x_value):
        self.x = x_value
        self.pos = (x_value, self.pos[1])
    
    def set_y(self, y_value):
        self.y = y_value
        self.pos = (self.pos[0], y_value)
    
    def draw(self, color):
        pygame.draw.circle(gameDisplay, color, (self.x, self.y), self.radius)

def sigmoid(x):
    return 1/(1+np.exp(-x))    

class Brain:
    def __init__(self, sight):
        self.nonlinear = sigmoid
        #3 layered input, first s inputs are for sight, next for the head position and last one for memory.
        self.l00 = [s[0] for s in sight] + [0] + [0]
        self.l01 = [s[1] for s in sight] + [0] + [0]
        self.l02 = [s[2] for s in sight] + [0] + [0]
        self.syn00 = 2*np.random.random((len(sight)+2,5)) - 1
        self.syn01 = 2*np.random.random((len(sight)+2,5)) - 1
        self.syn02 = 2*np.random.random((len(sight)+2,5)) - 1
        self.l1 = self.nonlinear(np.dot(self.l00, self.syn00) + np.dot(self.l01, self.syn01) + np.dot(self.l02, self.syn02))
        self.syn1 = 2*np.random.random((5,6)) - 1
        self.l2 = self.nonlinear(np.dot(self.l1, self.syn1))
   
    def update(self, sight, head):
        self.nonlinear = sigmoid
        self.l00 = [s[0] for s in sight] + [head] + [self.l2[3]]
        self.l01 = [s[1] for s in sight] + [head] + [self.l2[4]]
        self.l02 = [s[2] for s in sight] + [head] + [self.l2[5]]
        self.l1 = self.nonlinear(np.dot(self.l00, self.syn00) + np.dot(self.l01, self.syn01) + np.dot(self.l02, self.syn02))
        self.l2 = self.nonlinear(np.dot(self.l1, self.syn1))
        
    
    
class Walker:
    def __init__(self,
            name = "player 1" + str(time.time()%100000000), 
            x = None, 
            y = None, 
            color = pygame.Color("black") 
            #keys = (pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT)
            ):
        
        self.name = name
        
        if x == None:
            self.x = random.randint(0,display_width)
        else:
            self.x = x
        if y == None:
            self.y = random.randint(0,display_height)
        else:
            self.y = y
        
        self.circle = Circle(self.x,self.y,int(round(block_size/2)))
        self.pos = self.circle.pos
        self.sight_angle = 1
        self.resolution = 5
        self.sight = [pygame.Color("black") for _ in range(self.resolution)]
        self.brain = Brain(self.sight)
        self.health = 255
        self.birth = time.time()
        self.head = 0
        self.index = (min(width-1, self.x // line_of_sight), min(height-1, self.y // line_of_sight))
        cheap_distance_data_structure[self.index].append(self)
        
        self.angular_speed = 0
        self.angle = random.random() * 2 * math.pi
        self.speed = 0
        self.color = color
        
        #pygame.draw.circle(gameDisplay, self.color, (self.x, self.y), self.circle.radius*3)
        #self.up = keys[0]
        #self.right = keys[1]
        #self.down = keys[2]
        #self.left = keys[3]
    
    def set_x(self, x_value):
        x_value %= display_width
        self.x = x_value
        self.pos = (x_value, self.pos[1])
        self.circle.set_x(x_value)
        if self.index[0] != self.x // line_of_sight:
            cheap_distance_data_structure[self.index].remove(self)
            self.index = (min(width-1, self.x // line_of_sight), self.index[1])
            cheap_distance_data_structure[self.index].append(self)
    
    def set_y(self, y_value):
        y_value %= display_height
        self.y = y_value
        self.pos = (self.pos[0], y_value)
        self.circle.set_y(y_value)
        if self.index[1] != self.y // line_of_sight:
            cheap_distance_data_structure[self.index].remove(self)
            self.index = (self.index[0], min(height-1, self.y // line_of_sight))
            cheap_distance_data_structure[self.index].append(self)
    
    def is_in_view(self, target_pos):
        return is_in_sector(
            self.pos, 
            target_pos, 
            (self.angle + self.head - self.sight_angle) % (2 * math.pi), 
            (self.angle + self.head + self.sight_angle))
    
    def is_in_subview(self, target_pos, subview):
        #subview is the index which part of the sector should be asked
        part = (2 * self.sight_angle) / self.resolution
        left = part * subview
        right = left + part
        return is_in_sector(
            self.pos,
            target_pos,
            (self.angle + self.head - self.sight_angle + left) % (2 * math.pi),
            (self.angle + self.head - self.sight_angle + right))
            
    def draw_los_subview(self, color, subview):
        part = self.sight_angle / self.resolution * 2
        left = part * subview
        right = left + part
        drawsector(
            gameDisplay,
            color,
            self.pos,
            line_of_sight,
            (self.angle + self.head - self.sight_angle + left),
            (self.angle + self.head - self.sight_angle + right))
    
    def draw_los(self, color):
        drawsector(
            gameDisplay,
            color, 
            self.pos, 
            line_of_sight, 
            self.angle + self.head - sight_angle, 
            self.angle + self.head + sight_angle)
    def draw(self):
        self.circle.draw(self.color)
        #drawangularline(gameDisplay, pygame.Color("white"), self.pos, self.angle, line_of_sight/10)
        #drawangularline(gameDisplay, pygame.Color("yellow"), self.pos, self.angle + self.head, line_of_sight/5)


def walker_copy(walker):
    cp = copy.deepcopy(walker)
    cheap_distance_data_structure[cp.index].append(cp)
    cp.birth = time.time()
    cp.angle = cp.angle - math.pi
    cp.set_x(cp.x + random.randint(-10,10))
    cp.set_y(cp.y + random.randint(-10,10))
    cp.brain.syn00 += (np.random.random((cp.resolution+2,5)) - 0.5) / 5
    cp.brain.syn01 += (np.random.random((cp.resolution+2,5)) - 0.5) / 5
    cp.brain.syn02 += (np.random.random((cp.resolution+2,5)) - 0.5) / 5
    cp.brain.syn1 += (np.random.random((5,6)) - 0.5) / 5
    cp.color = pygame.Color("blue")
    return cp

class Apple:
    def __init__(self, x = None, y = None, color = None):
        if x == None:
            x = round(random.randrange(0, display_width - block_size))
        if y == None:
            y = round(random.randrange(0, display_height - block_size))
        self.circle = Circle(x,y,int(round(block_size/2)))
        self.pos = self.circle.pos
        self.x = self.circle.x
        self.y = self.circle.y
        if color == None:
            self.color = pygame.Color("green")
        else:
            self.color = color
        self.pos = self.circle.pos
        self.index = (min(width-1, self.x // line_of_sight), min(height-1, self.y // line_of_sight))
        cheap_distance_data_structure[self.index].append(self)

    def draw(self):
        self.circle.draw(self.color)

class Mine:
    def __init__(self, x = None, y = None, color = None):
        if x == None:
            x = round(random.randrange(0, display_width - block_size))
        if y == None:
            y = round(random.randrange(0, display_height - block_size))
        self.circle = Circle(x,y,int(round(block_size/2)))
        self.pos = self.circle.pos  
        self.x = self.circle.x
        self.y = self.circle.y
        if color == None:
            self.color = pygame.Color("red") 
        else:
            self.color = color
        self.pos = self.circle.pos
        self.index = (min(width-1, self.x // line_of_sight), min(height-1, self.y // line_of_sight))
        cheap_distance_data_structure[self.index].append(self)

    def draw(self):
        self.circle.draw(self.color)


def gameLoop():
    gameExit = False
    gameOver = (False, None)

    
    
    while not gameExit:
        while gameOver[0]:
            gameDisplay.fill(pygame.Color("black"))
            message_to_screen(gameOver[1] + " crashed, press C to play again or Q to quit", pygame.Color("red") )
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        gameExit = True
                        gameOver = (False, None)
                    if event.key == pygame.K_c:
                        gameLoop()
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameExit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                   with open("savegame", "rb") as f:
                       players, apples, mines, cheap_distance_data_structure = pickle.load(f)
                       player = players[0]
                   print("loaded!")
                if event.key == pygame.K_RETURN:
                    while(True):
                        for i,s in enumerate(player.sight):
                            inp = input("input " + str(i) + " : ")
                            inp = inp.split()
                            inp = [int(e) for e in inp]
                            player.sight[i] = pygame.Color(inp[0], inp[1], inp[2])
                        
                        player.brain.update(player.sight, player.head)
                        print(player.brain.l2)

    pygame.quit()
    quit()

gameLoop()

