import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import math, sys, random
import copy
class VisualField(object):
    """Visual Field of a Bot, 2"""
    def __init__(self,name, bot, width = 0, length = 0, radius = 0):# body of bot, not actual bot object
        self.bot = bot
        self.width = width
        self.length = length
        self.name = name
        self.radius = radius
    def AddToSpace(self, space, scale):
        self.width *= scale
        self.length *= scale
        self.radius *= scale
        self.body = pymunk.Body(0.0001 , 0.0001)
        self.vertices = [(0, 0) , (self.width, self.length/2), (self.width, -self.length/2)]
        if self.radius != 0:
            self.shape = pymunk.Circle(self.body, self.radius)
        else :
            self.shape = pymunk.Poly(self.body, self.vertices)
        self.shape._set_sensor(True)
        self.shape.collision_type = self.name
        self.body.position = self.bot.position + (self.width/2, 0)
        #self.shape.filter = pymunk.ShapeFilter(categories = 2)
        self.shape.color = pygame.color.THECOLORS["green"]
        self.pivotConstraint = pymunk.PivotJoint(self.bot, self.body, (0,0), (0,0))
        self.gearJoint = pymunk.GearJoint(self.bot, self.body,0 , 1)
        space.add(self.body,self.shape,  self.pivotConstraint, self.gearJoint)

