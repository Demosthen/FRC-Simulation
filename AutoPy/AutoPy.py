import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import math, sys, random
import Bot
import ScoreZone
import Retrievable
import Obstacle
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
## Balls
balls = []
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
bots = []
bots.append(Bot.Bot(pos = (3,5), color = "red"))
bots.append(Bot.Bot(pos = (3,(FIELD_WIDTH+1)/2), color = "red"))
bots.append(Bot.Bot(pos = (3,FIELD_WIDTH-3), color = "red"))
bots.append(Bot.Bot(pos = (FIELD_LENGTH-1,5), color = "blue"))
bots.append(Bot.Bot(pos = (FIELD_LENGTH-1,(FIELD_WIDTH+1)/2), color = "blue"))
bots.append(Bot.Bot(pos = (FIELD_LENGTH-1,FIELD_WIDTH-3), color = "blue"))
for i in range(NUM_BOTS):
    bots[i].AddToSpace(scale,space)
ticks_to_next_ball = 10
# add vaults
vaultZones = []
vaultZones.append(ScoreZone.ScoreZone(5,Vec2d((2.5,17.5)), 0, 3,4))
vaultZones.append(ScoreZone.ScoreZone(5,Vec2d((FIELD_LENGTH-0.5,FIELD_WIDTH-16.5)), 0, 3,4))
for zone in vaultZones:
    zone.AddToSpace(space, scale)
#add scale
scaleZones = []
scaleZones.append(ScoreZone.ScoreZone(10,Vec2d((28,20)),0,radius = 4))
scaleZones.append( ScoreZone.ScoreZone(10,Vec2d((28,9)),1,radius = 4))
for zone in scaleZones:
    zone.AddToSpace(space,scale)
# add physical scale barriers
scaleObs = []
scaleObs.append(Obstacle.Obstacle(Vec2d((28,14.5)), 1.792,10.79))
for obs in scaleObs:
    obs.AddToSpace(space,scale)
#space under scales (penalized because unpredictable scoring)
scalePenaltyZones = []
scalePenaltyZones.append(ScoreZone.ScoreZone(-10,Vec2d((28,20)),0,4,3,type = "penalty"))
scalePenaltyZones.append(ScoreZone.ScoreZone(-10,Vec2d((28,9)),1,4,3, type = "penalty"))
for zone in scalePenaltyZones:
    zone.AddToSpace(space,scale)
#add switches
switchZones = []
switchZones.append(ScoreZone.ScoreZone(10,Vec2d((15,21)),0,radius = 3))
switchZones.append(ScoreZone.ScoreZone(10,Vec2d((15,8)),1,radius = 3))
switchZones.append(ScoreZone.ScoreZone(10,Vec2d((41,21)),2,radius = 3))
switchZones.append(ScoreZone.ScoreZone(10,Vec2d((41,8)),3,radius = 3))
for zone in switchZones:
    zone.AddToSpace(space,scale)
#add physical switch walls
switchObs = []
switchObs.append(Obstacle.Obstacle(Vec2d((15,14.5)),3,12.75))
switchObs.append(Obstacle.Obstacle(Vec2d((41,14.5)),3,12.75))
for obs in switchObs:
    obs.AddToSpace(space,scale)
# add retrievable cubes
cubeName = "cube"
cubes = []
for i in range(10):
    cubes.append(Retrievable.Retrievable(cubeName, Vec2d(( random.uniform(-1,1)+12.125,14.5 + random.uniform(-1,1))),3,1.083,1.083)) # form group to simulate pyramid
    cubes.append(Retrievable.Retrievable(cubeName, Vec2d(( random.uniform(-1,1)+FIELD_LENGTH-11.125,14.5 + random.uniform(-1,1))),3,1.083,1.083))
for i in range(6):
    cubes.append(Retrievable.Retrievable(cubeName, Vec2d((16.875,20.354- i * 2.342)), 3,1.083,1.083))
    cubes.append(Retrievable.Retrievable(cubeName, Vec2d((FIELD_LENGTH-14.875,20.354- i * 2.342)), 3,1.083,1.083))
for cube in cubes:
    cube.AddToSpace(space,scale)
# add cube pickupZones
pickupZones = []
pickupZones.append(ScoreZone.ScoreZone(0, Vec2d((2,27)),0, radius = 1.5, type = "pickup"))
pickupZones.append(ScoreZone.ScoreZone(0, Vec2d((2,2)), 1, radius = 1.5, type="pickup"))
pickupZones.append(ScoreZone.ScoreZone(0, Vec2d((54,27)),2, radius = 1.5, type = "pickup"))
pickupZones.append(ScoreZone.ScoreZone(0, Vec2d((54,2)), 3, radius = 1.5, type="pickup"))
pickupZones.append(ScoreZone.ScoreZone(0, Vec2d((2.5,17.5)),2, 3,4, type = "pickup"))
pickupZones.append(ScoreZone.ScoreZone(0, Vec2d((FIELD_LENGTH-0.5,FIELD_WIDTH-16.5)), 3, 3,4, type="pickup"))
for zone in pickupZones:
    zone.AddToSpace(space,scale)
#main loop
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False
        elif event.type == KEYDOWN and event.key == K_p:
            pygame.image.save(screen, "bouncing_balls.png")
            
    
    ### Clear screen
    screen.fill(THECOLORS["white"])
    
    ### Draw stuff
    bots[1].TurnLeft(5)
    temp = bots[1].CheckInFront(space)
    space.debug_draw(draw_options)

    ### Update physics
    dt = 1.0/60.0
    for x in range(1):
        space.step(dt)
    
    ### Flip screen
    pygame.display.flip()
    clock.tick(30)#fps
    pygame.display.set_caption("fps: " + str(clock.get_fps()))
    #NOTES:
    #shape_query(shape)[source] or collisionhandler for point assignment
    #rename ScoreZone to Zone object later
    #better to undestimate visual field bc convnet can mislabel at edges