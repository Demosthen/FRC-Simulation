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
import time
from Global import *
#Lengths are in ft and masses are in lbs
pygame.init()
screen = pygame.display.set_mode((1200, 600))
clock = pygame.time.Clock()
running = True

### Physics stuff
space = pymunk.Space()

space.gravity = (0.0, 0.0)
draw_options = pymunk.pygame_util.DrawOptions(screen)
penaltyCounter = 0
canForce = False
canLevitate = False
canBoost = False
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
def beginBotVault(arbiter, space, data):
    data[arbiter.shapes[0]._get_shapeid()].canScore = True
    data[arbiter.shapes[0]._get_shapeid()].canPickup = True
    return True
def endBotVault(arbiter, space, data):
    data[arbiter.shapes[0]._get_shapeid()].canScore = False
    data[arbiter.shapes[0]._get_shapeid()].canPickup = False
    return True
def beginPenaltyBot(arbiter, space, data):
    data[arbiter.shapes[1]._get_shapeid()].GivePoints(space,data[arbiter.shapes[0]._get_shapeid()], -10 )
    return True

def duringPenaltyBot(arbiter, space, data):
    data[arbiter.shapes[0]._get_shapeid()].penaltyTime += 10
    return True
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

def AddObjects(list):
    for elem in list:
        objects[elem.shape._get_shapeid()] = elem

def scaleScore(space, scaleZones):#call every second pls
    if scaleZones[int(scaleZones[0].numRet < scaleZones[1].numRet)].color == "red":
        redScore.val += SCALE_POINTS * int(not scaleZones[0].numRet == scaleZones[1].numRet)
    else:
        blueScore.val += SCALE_POINTS * int(not scaleZones[0].numRet == scaleZones[1].numRet)
def switchScore(space, switchZones):#call every second pls
    if switchZones[int(switchZones[0].numRet < switchZones[1].numRet)].color == "red":
        redScore.val += SCALE_POINTS * int(not switchZones[0].numRet == switchZones[1].numRet)
    else:
        blueScore.val += SCALE_POINTS * int(not switchZones[0].numRet == switchZones[1].numRet)
def vaultScore(space, vaultZones):# per cube
    redIndex = int(vaultZones[1].color == "red") 
    redScore.val += VAULT_POINTS * vaultZones[redIndex].numRet
    blueScore.val += VAULT_POINTS * vaultZones[1-redIndex].numRet
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
    line.elasticity = 0
    line.friction = 0.9
    line.filter = pymunk.ShapeFilter(categories = 1, mask = pymunk.ShapeFilter.ALL_MASKS ^ 2)
space.add(field)

#add bots
bots = []
scaleColor, switchColor = getColors()
bots.append(Bot(BOT_NAME,pos = Vec2d((3,5)), color = "red",score = redScore))
bots.append(Bot(BOT_NAME,pos = Vec2d((3,(FIELD_WIDTH+1)/2)), color = "red",score = redScore))
bots.append(Bot(BOT_NAME,pos = Vec2d(3,FIELD_WIDTH-3), color = "red", score = redScore))
bots.append(Bot(BOT_NAME,pos = Vec2d(FIELD_LENGTH-1,5), color = "blue", score = blueScore))
bots.append(Bot(BOT_NAME,pos = Vec2d(FIELD_LENGTH-1,(FIELD_WIDTH+1)/2), color = "blue", score = blueScore))
bots.append(Bot(BOT_NAME,pos = Vec2d(FIELD_LENGTH-1,FIELD_WIDTH-3), color = "blue", score = blueScore))

# add vaults
vaults = []
vaults.append(ScoreZone(VAULT_NAME, 5,Vec2d((2.5,17.5)), True, False, True,"red", 3,4,retKey = VAULT_RETKEY))
vaults.append(ScoreZone(VAULT_NAME, 5,Vec2d((FIELD_LENGTH-0.5,FIELD_WIDTH-16.5)), True, False, True,"blue", 3,4,retKey = VAULT_RETKEY))

#add scale
scales = []
scales.append(ScoreZone(SCALE_NAME,10,Vec2d((28,20)),True,False,False,scaleColor[0],radius = 4, retKey = SCALE_RETKEY))
scales.append(ScoreZone(SCALE_NAME,10,Vec2d((28,9)),True, False, False,scaleColor[1],radius = 4, retKey = SCALE_RETKEY))

# add physical scale barriers
scaleBarriers = []
scaleBarriers.append(Obstacle(OBSTACLE_NAME,Vec2d((28,14.5)), 1.792,10.79))

#space under scales (penalized because unpredictable scoring)
scalePenalties = []
scalePenalties.append(ScoreZone(PENALTY_NAME,-10,Vec2d((28,20)),False, True, False,scaleColor[0],4,3))
scalePenalties.append(ScoreZone(PENALTY_NAME,-10,Vec2d((28,9)),False, True, False,scaleColor[1],4,3))

#add switches
switches = []
switches.append(ScoreZone(SWITCH_NAME,10,Vec2d((15,21)),True, False, False,switchColor[0], radius = 3, retKey = SWITCH_RETKEY))
switches.append(ScoreZone(SWITCH_NAME,10,Vec2d((15,8)),True, False, False,switchColor[1],radius = 3, retKey = SWITCH_RETKEY))
switches.append(ScoreZone(SWITCH_NAME,10,Vec2d((41,21)),True, False, False,switchColor[0],radius = 3, retKey = SWITCH_RETKEY))
switches.append(ScoreZone(SWITCH_NAME,10,Vec2d((41,8)),True, False, False,switchColor[1],radius = 3, retKey = SWITCH_RETKEY))

#add physical switch walls
switchBarriers = []
switchBarriers.append(Obstacle(OBSTACLE_NAME,Vec2d((15,14.5)),3,12.75))
switchBarriers.append(Obstacle(OBSTACLE_NAME,Vec2d((41,14.5)),3,12.75))

# add retrievable cubes
cubes = []
for i in range(10):
    cubes.append(Retrievable(CUBE_NAME, Vec2d(( random.uniform(-1,1)+12.125,14.5 + random.uniform(-1,1))),3,1.083,1.083)) # form group to simulate pyramid
    cubes.append(Retrievable(CUBE_NAME, Vec2d(( random.uniform(-1,1)+FIELD_LENGTH-11.125,14.5 + random.uniform(-1,1))),3,1.083,1.083))

for i in range(6):
    cubes.append(Retrievable(CUBE_NAME, Vec2d((16.875,20.354- i * 2.342)), 3,1.083,1.083))
    cubes.append(Retrievable(CUBE_NAME, Vec2d((FIELD_LENGTH-14.875,20.354- i * 2.342)), 3,1.083,1.083))

# add cube pickupZones
cubePickup = []
cubePickup.append(ScoreZone(PICKUP_NAME,0, Vec2d((2,FIELD_LENGTH/2)),False, False, True,"blue", radius = 1.5))
cubePickup.append(ScoreZone(PICKUP_NAME,0, Vec2d((2,2)), False, False, True,"blue", radius = 1.5))
cubePickup.append(ScoreZone(PICKUP_NAME,0, Vec2d((FIELD_LENGTH,FIELD_LENGTH/2)),False, False, True,"red", radius = 1.5))
cubePickup.append(ScoreZone(PICKUP_NAME,0, Vec2d((FIELD_LENGTH,2)), False, False, True,"red", radius = 1.5))

#add everything to space
for key, zone in objects.items():
     zone.AddToSpace(space)

#set collision handlers
botSwitch = space.add_collision_handler(collision_types[BOT_NAME], collision_types[SWITCH_NAME])
botSwitch.data.update(objects)
botSwitch.pre_solve = beginBotScore
botSwitch.separate = endBotScore
botScale = space.add_collision_handler(collision_types[BOT_NAME], collision_types[SCALE_NAME])
botScale.data.update(objects)
botScale.pre_solve = beginBotScore
botScale.separate = endBotScore
botVault = space.add_collision_handler(collision_types[BOT_NAME], collision_types[VAULT_NAME])
botVault.data.update(objects)
botVault.pre_solve  = beginBotVault
botVault.separate = endBotVault
botBot = space.add_collision_handler(collision_types[BOT_NAME], collision_types[BOT_NAME])
botBot.data.update(objects)
botBot.pre_solve = duringBotBot
botPickup = space.add_collision_handler(collision_types[BOT_NAME], collision_types[PICKUP_NAME])
botPickup.data.update(objects)
botPickup.pre_solve  = beginBotPickup
botPickup.separate = endBotPickup

#main loop
secs = 0
prevTime = time.time()
while running:
    for event in pygame.event.get():
        # debug input
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
                zones = bots[1].ScoreZoneCheck(space)
                if len(zones) > 0:
                    bots[1].DropOff(space, bots[1].rets[CUBE_NAME][0], zones[0])
                else:
                    bots[1].DropOff(space, bots[1].rets[CUBE_NAME][0])
        elif event.type == KEYDOWN and event.key == K_q:
            bots[1].PickUp(space, bots[1].GetClosestRet(space))
        elif event.type == KEYDOWN and event.key == K_r:
            scales[0].numRet += 1
        elif event.type == KEYDOWN and event.key == K_f:
            vaultScore(space, vaults)
    ### Clear screen
    screen.fill(THECOLORS["white"])

    ### Draw stuff
    space.debug_draw(draw_options)

    ## Update physics, move forward 1/60 second
    dt = 1.0/STEP_SIZE
    for x in range(1):
        space.step(dt)
    #update scores each second
    t = time.time()
    if math.floor(t) > prevTime:
        scaleScore(space, scales)
        switchScore(space, switches)
        secs+=1
        prevTime = t
    ### Flip screen
    pygame.display.flip()
    clock.tick()#fps
    pygame.display.set_caption("fps: " + str(clock.get_fps()) + " red: " + str(redScore.val) + " blue: " + str(blueScore.val))
    #NOTES:
    #test
    #shape_query(shape)[source] or collisionhandler for point assignment
    #consolidate overlapping zones
    #organize rets into named dict
    #rename ScoreZone to Zone object later
    #better to undestimate visual field bc convnet can mislabel at edges