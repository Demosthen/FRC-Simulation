import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import math, sys, random
class ScoreZone(object):# rename to Zone object later
    """Score Zone (Penalty Zone if score is negative), 5"""
    def __init__(self, score, pos, id, width=0, length=0, radius = 0, type = "score", retKey = []):
        self.score = score
        self.width = width
        self.length = length
        self.radius = radius
        self.id = id # int
        self.pos = pos
        self.type = type
        self.numRet = 0
        self.retKey = retKey
    def AddToSpace(self, space,scale):
        self.body = pymunk.Body(0.001,0.001)# low mass/inertia so doesn't affect retrievable movement
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
        self.shape.filter = pymunk.ShapeFilter(categories = 5)
        if self.type == "penalty":
            self.shape.color = pygame.color.THECOLORS["pink"]
        elif self.type == "pickup":
            self.shape.color = pygame.color.THECOLORS["orange"]
        else:
            self.shape.color = pygame.color.THECOLORS["purple"]
        space.add(self.body, self.shape)
    def GetRet(self, space, bot):
        hi
        self.numRet += 1

    def GivePoints(self, space, bot, zones):
        hi
    def Constrain(self, space, object):
        constraint = pymunk.PivotJoint(self.body, object, (0,0), (0,0))
        space.add(constraint)

