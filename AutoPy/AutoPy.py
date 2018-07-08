import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import math, sys, random
from collections import defaultdict
from Bot import Bot
from ScoreZone import ScoreZone
from Retrievable import Retrievable
from Obstacle import Obstacle
from Int import Int
from copy import copy
#Lengths are in ft and masses are in lbs
pygame.init()
screen = pygame.display.set_mode((1200, 600))
clock = pygame.time.Clock()
running = True
scale = 20
### Physics stuff
space = pymunk.Space()
space.gravity = (0.0, 0.0)
draw_options = pymunk.pygame_util.DrawOptions(screen)
NUM_BOTS = 6
NUM_ZONES = 2
NUM_RET = 20
FIELD_WIDTH = 27
FIELD_LENGTH = 54

BOT_NAME = "Bot"
PICKUP_NAME = "Pickup"
SCALE_NAME = "Scale"
VAULT_NAME = "Vault"
SWITCH_NAME = "Switch"
PENALTY_NAME = "Penalty"
OBSTACLE_NAME = "Obstacle"
CUBE_NAME = "Cube"
VISFIELD_NAME = "VisField"
penaltyCounter = 0
collision_types = {BOT_NAME:1,
                   PICKUP_NAME:2,
                   SCALE_NAME:3,
                   VAULT_NAME:4,
                   SWITCH_NAME:5,
                   PENALTY_NAME:6,
                   OBSTACLE_NAME:7,
                   CUBE_NAME:8,
                   VISFIELD_NAME:9}

def beginBotPickup(arbiter, space, data):
    data[arbiter.shapes[0]._get_shapeid()].canPickup = True
    return True

def endBotPickup(arbiter, space, data):
    data[arbiter.shapes[0]._get_shapeid()].canPickup = False
    return True

def beginBotScore(arbiter, space, data):
    data[arbiter.shapes[0]._get_shapeid()].canScore = True
    return True

def endBotScore(arbiter, space, data):
    data[arbiter.shapes[0]._get_shapeid()].canScore = False
    return True

def beginPenaltyBot(arbiter, space, data):
    data[arbiter.shapes[1]._get_shapeid()].GivePoints(space,data[arbiter.shapes[0]._get_shapeid()], -10 )
    return True

def duringPenaltyBot(arbiter, space, data):
    data[arbiter.shapes[0]._get_shapeid()].penaltyTime += 10

def duringBotBot(arbiter, space, data):
    return True
def getColors():
    """return scale and switch colors in that order"""
    switch = ["red", "blue"]
    if random.random() >= 0.5:
        switch[0], switch[1] = switch[1], switch[0]
    scale = ["red", "blue"]
    if random.random() >= 0.5:
        scale[0], scale[1] = scale[1], scale[0]
    return scale, switch
def scaleScore(space, scaleZones):
       placeholder
static_body = space.static_body
#add field walls
field = [pymunk.Segment(static_body, (scale*1.0,scale*1.0), (scale*(FIELD_LENGTH+1),scale*1.0), 0.0),# add 1 to dims to offset field
                pymunk.Segment(static_body, (scale*1.0,scale*1.0), (scale*1.0,scale*(FIELD_WIDTH+1)),0.0),
                pymunk.Segment(static_body, (scale*(FIELD_LENGTH+1),scale*1.0), (scale*(FIELD_LENGTH+1),scale*(FIELD_WIDTH+1)), 0.0),
                pymunk.Segment(static_body,(scale*1.0,scale*(FIELD_WIDTH+1)),(scale*(FIELD_LENGTH+1),scale*(FIELD_WIDTH+1)),0.0),
                pymunk.Segment(static_body, (scale*1.0,scale*2.401), (scale*(3.714),scale*1.0), 0.0),
                pymunk.Segment(static_body, (scale*(FIELD_LENGTH+1),scale*2.401), (scale*(FIELD_LENGTH - 2.714),scale*1.0), 0.0),
                pymunk.Segment(static_body, (scale*1.0,scale*(FIELD_WIDTH - 0.401)), (scale*(3.714),scale*FIELD_WIDTH+1), 0.0),
                pymunk.Segment(static_body, (scale*(FIELD_LENGTH+1),scale*(FIELD_WIDTH - 0.401)), (scale*(FIELD_LENGTH - 1.714),scale*(FIELD_WIDTH+1)), 0.0)]
for line in field:
    line.elasticity = 0.95
    line.friction = 0.9
    line.filter = pymunk.ShapeFilter(categories = 1, mask = pymunk.ShapeFilter.ALL_MASKS ^ 2)
space.add(field)
#add bots
redScore = Int(0)
blueScore = Int(0)
objects = defaultdict(lambda:None)
bots = []
scaleColor, switchColor = getColors()
bots.append(Bot(BOT_NAME,pos = Vec2d((3,5)), color = "red",score = redScore, scale = scale))
bots.append(Bot(BOT_NAME,pos = Vec2d((3,(FIELD_WIDTH+1)/2)), color = "red",score = redScore, scale = scale))
bots.append(Bot(BOT_NAME,pos = Vec2d(3,FIELD_WIDTH-3), color = "red", score = redScore, scale = scale))
bots.append(Bot(BOT_NAME,pos = Vec2d(FIELD_LENGTH-1,5), color = "blue", score = blueScore, scale = scale))
bots.append(Bot(BOT_NAME,pos = Vec2d(FIELD_LENGTH-1,(FIELD_WIDTH+1)/2), color = "blue", score = blueScore, scale = scale))
bots.append(Bot(BOT_NAME,pos = Vec2d(FIELD_LENGTH-1,FIELD_WIDTH-3), color = "blue", score = blueScore, scale = scale))
for i in range(NUM_BOTS):
    objects[bots[i].shape._get_shapeid()] = bots[i]
    objects[bots[i].VisField.shape._get_shapeid()] = bots[i]
ticks_to_next_ball = 10

# add vaults
temp = ScoreZone(VAULT_NAME, 5,Vec2d((2.5,17.5)), True, False, True,"red",scale, 3,4)
objects[temp.shape._get_shapeid()]=(temp)
temp = ScoreZone(VAULT_NAME, 5,Vec2d((FIELD_LENGTH-0.5,FIELD_WIDTH-16.5)), True, False, True,"blue",scale, 3,4)
objects[temp.shape._get_shapeid()]=(temp)

#add scale
temp = ScoreZone(SCALE_NAME,10,Vec2d((28,20)),True,False,False,scaleColor[0], scale,radius = 4)
objects[temp.shape._get_shapeid()]=(temp)
temp =  ScoreZone(SCALE_NAME,10,Vec2d((28,9)),True, False, False,scaleColor[1],scale,radius = 4)
objects[temp.shape._get_shapeid()]=(temp)

# add physical scale barriers
temp = Obstacle(OBSTACLE_NAME,Vec2d((28,14.5)),scale, 1.792,10.79)
objects[temp.shape._get_shapeid()]=(temp)
#space under scales (penalized because unpredictable scoring)
temp = ScoreZone(PENALTY_NAME,-10,Vec2d((28,20)),False, True, False,scaleColor[0],scale,4,3)
objects[temp.shape._get_shapeid()]=(temp)
temp = ScoreZone(PENALTY_NAME,-10,Vec2d((28,9)),False, True, False,scaleColor[1],scale,4,3)
objects[temp.shape._get_shapeid()]=(temp)
#add switches
temp = ScoreZone(SWITCH_NAME,10,Vec2d((15,21)),True, False, False,switchColor[0],scale, radius = 3)
objects[temp.shape._get_shapeid()]=(temp)
temp = ScoreZone(SWITCH_NAME,10,Vec2d((15,8)),True, False, False,switchColor[1],scale,radius = 3)
objects[temp.shape._get_shapeid()]=(temp)
temp = ScoreZone(SWITCH_NAME,10,Vec2d((41,21)),True, False, False,switchColor[0],scale,radius = 3)
objects[temp.shape._get_shapeid()]=(temp)
temp = ScoreZone(SWITCH_NAME,10,Vec2d((41,8)),True, False, False,switchColor[1],scale,radius = 3)
objects[temp.shape._get_shapeid()]=(temp)
#add physical switch walls
temp = Obstacle(OBSTACLE_NAME,Vec2d((15,14.5)),scale,3,12.75)
objects[temp.shape._get_shapeid()]=(temp)
temp = Obstacle(OBSTACLE_NAME,Vec2d((41,14.5)),scale,3,12.75)
objects[temp.shape._get_shapeid()]=(temp)
# add retrievable cubes
for i in range(10):
    temp = Retrievable(CUBE_NAME, Vec2d(( random.uniform(-1,1)+12.125,14.5 + random.uniform(-1,1))),scale,3,1.083,1.083) # form group to simulate pyramid
    objects[temp.shape._get_shapeid()]=(temp)
    objects[temp.pickupZone.shape._get_shapeid()] = temp
    sample = temp.pickupZone
    temp = Retrievable(CUBE_NAME, Vec2d(( random.uniform(-1,1)+FIELD_LENGTH-11.125,14.5 + random.uniform(-1,1))),scale,3,1.083,1.083)
    objects[temp.shape._get_shapeid()]=(temp)
    objects[temp.pickupZone.shape._get_shapeid()] = temp
for i in range(6):
    temp = Retrievable(CUBE_NAME, Vec2d((16.875,20.354- i * 2.342)),scale, 3,1.083,1.083)
    objects[temp.shape._get_shapeid()]=(temp)
    objects[temp.pickupZone.shape._get_shapeid()] = temp
    temp = Retrievable(CUBE_NAME, Vec2d((FIELD_LENGTH-14.875,20.354- i * 2.342)),scale, 3,1.083,1.083)
    objects[temp.shape._get_shapeid()]=(temp)
    objects[temp.pickupZone.shape._get_shapeid()] = temp
# add cube pickupZones
temp = ScoreZone(PICKUP_NAME,0, Vec2d((2,FIELD_LENGTH/2)),False, False, True,scale, radius = 1.5)
objects[temp.shape._get_shapeid()]=(temp)
temp = ScoreZone(PICKUP_NAME,0, Vec2d((2,2)), False, False, True,scale, radius = 1.5)
objects[temp.shape._get_shapeid()]=(temp)
temp = ScoreZone(PICKUP_NAME,0, Vec2d((FIELD_LENGTH,FIELD_LENGTH/2)),False, False, True,scale, radius = 1.5)
objects[temp.shape._get_shapeid()]=(temp)
temp = ScoreZone(PICKUP_NAME,0, Vec2d((FIELD_LENGTH,2)), False, False, True,scale, radius = 1.5)
objects[temp.shape._get_shapeid()]=(temp)
for key, zone in objects.items():
    if zone.shape.space == None:
        zone.AddToSpace(space, collision_types)

botSwitch = space.add_collision_handler(collision_types[BOT_NAME], collision_types[SWITCH_NAME])
botSwitch.data.update(objects)
botSwitch.begin = beginBotScore
botSwitch.separate = endBotScore
botScale = space.add_collision_handler(collision_types[BOT_NAME], collision_types[SCALE_NAME])
botScale.data.update(objects)
botScale.begin = beginBotScore
botScale.end = endBotScore
botBot = space.add_collision_handler(collision_types[BOT_NAME], collision_types[BOT_NAME])
botBot.data.update(objects)
botBot.pre_solve = duringBotBot
botPickup = space.add_collision_handler(collision_types[BOT_NAME], collision_types[PICKUP_NAME])
botPickup.data.update(objects)
botPickup.begin = beginBotPickup
botPickup.separate = endBotPickup
#sample.AddToSpace(space, collision_types)
#main loop
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False
        elif event.type == KEYDOWN and event.key == K_p:
            pygame.image.save(screen, "bouncing_balls.png")
        elif event.type == KEYDOWN and event.key == K_w:
            bots[1].Forward(100)
        elif event.type == KEYDOWN and event.key == K_d:
            bots[1].TurnRight(100)
        elif event.type == KEYDOWN and event.key == K_a:
            bots[1].TurnLeft(100)
        elif event.type == KEYDOWN and event.key == K_s:
            bots[1].Backward(100)
        elif event.type == KEYDOWN and event.key == K_e:
            if len(bots[1].rets[CUBE_NAME]) > 0:
                bots[1].DropOff(space, bots[1].rets[CUBE_NAME][0])
        elif event.type == KEYDOWN and event.key == K_q:
            bots[1].PickUp(space, bots[1].GetClosestRet(space, objects))
    
    ### Clear screen
    screen.fill(THECOLORS["white"])
    ### Draw stuff
    space.debug_draw(draw_options)

    ##
    ## Update physics
    dt = 1.0/60.0
    for x in range(1):
        space.step(dt)
    
    ### Flip screen
    pygame.display.flip()
    clock.tick(30)#fps
    pygame.display.set_caption("fps: " + str(clock.get_fps()))
    #NOTES:
    #test
    #shape_query(shape)[source] or collisionhandler for point assignment
    #consolidate overlapping zones
    #rename ScoreZone to Zone object later
    #subclass shape or hash by shape ids (2DONE)
    #assign points by team, not by bot
    #better to undestimate visual field bc convnet can mislabel at edges