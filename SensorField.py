import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import math, sys, random
import copy
from Global import *
class SensorField(object):
    """Sensory Field of a Bot"""
    def __init__(self, name, context, bot, width = 0, length = 0, radius = 0, owner = None):# body of bot, not actual bot passed as param
        #set initial variables
        self.context = context
        self.bot = bot
        self.owner = owner
        self.width = width * SCALE
        self.length = length * SCALE
        self.name = name
        self.scale = SCALE
        self.radius = radius * SCALE
        self.body = pymunk.Body(0.0001 , 0.0001)
        self.vertices = [(0, 0) , (self.width, self.length/2), (self.width, -self.length/2)]
        if self.radius != 0:
            self.shape = pymunk.Circle(self.body, self.radius)
        else :
            self.shape = pymunk.Poly(self.body, self.vertices)
        self.shape._set_sensor(True)
        self.body.position = self.bot.position + (self.width/2, 0)
        #self.shape.filter = pymunk.ShapeFilter(categories = 2)
        self.shape.color = pygame.color.THECOLORS["green"]
        self.context.objects[self.shape._get_shapeid()] = self
        self.shape.collision_type = collision_types[self.name]

    def AddToSpace(self):
        if self.shape.space == None:
            #constrain to bot's body
            self.pivotConstraint = pymunk.PivotJoint(self.bot, self.body, (0,0), (0,0))
            self.gearJoint = pymunk.GearJoint(self.bot, self.body,0 , 1)
            self.context.space.add(self.body,self.shape,  self.pivotConstraint, self.gearJoint)

    def CleanUp(self):
        self.context.objects.pop(self.shape._get_shapeid())
        self.context.space.remove(self.shape, self.body, self.pivotConstraint, self.gearJoint)