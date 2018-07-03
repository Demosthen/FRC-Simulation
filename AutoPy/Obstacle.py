import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import math, sys, random
class Obstacle(object):
    """immovable collidable obstacle, 4"""
    def __init__(self, pos, width, length, radius = 0):
        self.pos = pos
        self.width = width
        self.length = length
        self.radius = radius
    def AddToSpace(self, space, scale):
        body = pymunk.Body(body_type = pymunk.cp.CP_BODY_TYPE_STATIC)
        self.pos *=scale
        body.position = self.pos
        self.width*=scale
        self.length*=scale
        self.radius*=scale
        self.vertices = [(-self.width/2, -self.length/2), (-self.width/2, self.length/2), (self.width/2,self.length/2),(self.width/2,-self.length/2)]
        if self.radius != 0:
            self.shape = pymunk.Circle(body, self.radius)
        else :
            self.shape = pymunk.Poly(body, self.vertices)
        self.shape.filter = pymunk.ShapeFilter(categories = 4)
        self.shape.color = pygame.color.THECOLORS["gray"]
        space.add(body, self.shape)


