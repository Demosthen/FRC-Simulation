import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import math, sys, random
class Obstacle(object):
    """immovable collidable obstacle, 4"""
    def __init__(self,name,  pos, scale,  width, length, radius = 0):
        self.name = name
        self.pos = pos * scale
        self.width = width * scale
        self.length = length * scale
        self.radius = radius * scale
        self.body = pymunk.Body(body_type = pymunk.cp.CP_BODY_TYPE_STATIC)
        self.body.position = self.pos
        self.isPickup = False
        self.scale = scale
        self.vertices = [(-self.width/2, -self.length/2), (-self.width/2, self.length/2), (self.width/2,self.length/2),(self.width/2,-self.length/2)]
        if self.radius != 0:
            self.shape = pymunk.Circle(self.body, self.radius)
        else :
            self.shape = pymunk.Poly(self.body, self.vertices)
        #self.shape.filter = pymunk.ShapeFilter(categories = 1)
        self.shape.color = pygame.color.THECOLORS["gray"]
    def AddToSpace(self, space, key):
        self.shape.collision_type = key[self.name]
        space.add(self.body, self.shape)


