import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import math, sys, random
class ScoreZone(object):# rename to Zone object later
    """Score Zone (Penalty Zone if score is negative), 5"""
    inv = defaultdict(lambda:None)
    def __init__(self,name, score, pos, isScore, isPenalty, isPickup, scale = 1 ,width=0, length=0, radius = 0, retKey = []):
        self.score = score
        self.name = name
        self.width = width
        self.length = length
        self.radius = radius
        self.pos = pos
        self.type = type
        self.numRet = 0
        self.retKey = retKey
        self.isScore = isScore
        self.isPenalty = isPenalty
        self.isPickup = isPickup
        self.body = pymunk.Body(0.000001,0.001)# low mass/inertia so doesn't affect retrievable movement
        self.pos *=scale
        self.body.position = self.pos
        self.width*=scale
        self.length*=scale
        self.radius*=scale
        self.vertices = [(-self.width/2, -self.length/2), (-self.width/2, self.length/2), (self.width/2,self.length/2),(self.width/2,-self.length/2)]
        if self.radius != 0:
            self.shape = pymunk.Circle(self.body, self.radius)
        else :
            self.shape = pymunk.Poly(self.body, self.vertices)
            
        self.shape._set_sensor(True)
        self.shape.collision_type = self.name
        #self.shape.filter = pymunk.ShapeFilter(categories = 2)
        if self.isPenalty:
            self.body.body_type = pymunk.cp.CP_BODY_TYPE_STATIC
            self.shape.color = pygame.color.THECOLORS["pink"]
        elif self.isPickup:
            self.body.body_type = pymunk.cp.CP_BODY_TYPE_DYNAMIC
            self.shape.color = pygame.color.THECOLORS["orange"]
        else:
            self.body.body_type = pymunk.cp.CP_BODY_TYPE_STATIC
            self.shape.color = pygame.color.THECOLORS["purple"]
    def AddToSpace(self, space):
        space.add(self.body, self.shape)
    def GetRet(self, space, bot, retrievable):
        self.inv[retrievable.name] = retrievable
        self.numRet += 1
    def GivePoints(self, space, bot,points, zones):
        hi
    def Constrain(self, space, object):
        constraint = pymunk.PivotJoint(self.body, object, (0,0), (0,0))
        space.add(constraint)

