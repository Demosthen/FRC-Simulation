import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from collections import defaultdict
from pymunk import Vec2d
import math, sys, random
from Global import *
from Retrievable import Retrievable
from Bot import Bot
class ScoreZone(object):# rename to Zone object later
    """Score Zone (Penalty Zone if score is negative), 5"""
    
    def __init__(self,name,context, pos, isScore, isPenalty, isPickup, color = "none", width=0, length=0, radius = 0, retKey = defaultdict()):
        self.name = name
        self.context = context
        self.scale = SCALE
        self.width = width * SCALE
        self.length = length * SCALE
        self.radius = radius * SCALE
        self.pos = pos * SCALE
        self.color = color
        self.numRet = 0
        self.retKey = retKey
        self.isScore = isScore
        self.isPenalty = isPenalty
        self.isPickup = isPickup
        self.body = pymunk.Body(0.000001,0.001)# low mass/inertia so doesn't affect retrievable movement
        self.body.position = self.pos
        self.vertices = [(-self.width/2, -self.length/2), (-self.width/2, self.length/2), (self.width/2,self.length/2),(self.width/2,-self.length/2)]
        if self.radius != 0:
            self.shape = pymunk.Circle(self.body, self.radius)
        else :
            self.shape = pymunk.Poly(self.body, self.vertices)
        self.shape._set_sensor(True)
        if self.isPenalty:
            self.body.body_type = pymunk.cp.CP_BODY_TYPE_STATIC
            self.shape.color = pygame.color.THECOLORS["pink"]
        elif self.isPickup:
            self.body.body_type = pymunk.cp.CP_BODY_TYPE_DYNAMIC
            self.shape.color = pygame.color.THECOLORS["orange"]
        else:
            self.body.body_type = pymunk.cp.CP_BODY_TYPE_STATIC
            self.shape.color = pygame.color.THECOLORS["purple"]
        if self.color == "red":
            self.score = self.context.redScore
        else:
            self.score = self.context.blueScore
        #put object into registry
        self.context.objects[self.shape._get_shapeid()] = self
        self.shape.collision_type = collision_types[self.name]
        self.inv = defaultdict(lambda:[])
        self.penaltyTime = 0
        self.inSpace = False

    def AddToSpace(self):
        if not self.inSpace:
            self.context.space.add(self.body, self.shape)
            self.inSpace = True

    def GetRet(self, bot, retrievable):
        self.inv[retrievable.name].append(retrievable)
        self.numRet += 1

    def GiveRet(self, bot, retName):
        newRet = Retrievable(retName,self.context, self.pos,3,1.083,1.083)
        newRet.AddToSpace()
        return newRet

    def GivePoints(self, bot,points):
        hi

    def Constrain(self, object):
        self.context.objects[self.shape._get_shapeid()] = object
        self.constraint = pymunk.PivotJoint(self.body, object.body, (0,0), (0,0))
        self.context.space.add(self.constraint)

