import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import math, sys, random
import copy
from Global import *
class VisualField(object):
    """Visual Field of a Bot, 2"""
    def __init__(self,name, bot, width = 0, length = 0, radius = 0):# body of bot, not actual bot object
        #set initial variables
        self.bot = bot
        self.width = width * scale
        self.length = length * scale
        self.name = name
        self.scale = scale
        self.radius = radius * scale
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
        objects[self.shape._get_shapeid()] = self
        self.shape.collision_type = collision_types[self.name]
    def AddToSpace(self, space):
        if self.shape.space == None:
            #constrain to bot's body
            self.pivotConstraint = pymunk.PivotJoint(self.bot, self.body, (0,0), (0,0))
            self.gearJoint = pymunk.GearJoint(self.bot, self.body,0 , 1)
            space.add(self.body,self.shape,  self.pivotConstraint, self.gearJoint)

