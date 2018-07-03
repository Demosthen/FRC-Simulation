import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import math, sys, random
import copy
import ScoreZone
class Retrievable(object):
    """Retrievable object (Power Cube, whiffle ball, etc), 3"""
    def __init__(self, name, initPos, mass, width, length, radius = 0): # if num provided for radius, circle assumed
        self.name = name
        self.mass = mass
        self.width=width
        self.length = length
        self.pos = initPos
        self.radius = radius
        self.pickupZone = ScoreZone.ScoreZone(0,copy.deepcopy(self.pos),0,radius = 1, type = "pickup")
    def AddToSpace(self, space, scale):
        self.width*=scale
        self.length*=scale
        self.radius *= scale
        self.pos *= scale
        points = [(-self.width/2, -self.length/2),(-self.width/2,self.length/2),(self.width/2,self.length/2),(self.width/2,-self.length/2)]
        if self.radius > 0:
            self.inertia = pymunk.moment_for_circle(self.mass,self.radius,self.radius)
            self.body = pymunk.Body(self.mass,self.inertia)
            self.shape = pymunk.Circle(self.body,self.radius)
        else:
            self.inertia = pymunk.moment_for_poly(self.mass,points)
            self.body = pymunk.Body(self.mass, self.inertia)
            self.shape = pymunk.Poly(self.body, points)
        self.body.position = self.pos
        self.shape.elasticity = 0.95
        self.shape.friction = 0.9
        self.shape.filter = pymunk.ShapeFilter(categories = 3)
        self.shape.color = pygame.color.THECOLORS["yellow"]
        self.pickupZone.AddToSpace(space,scale)
        space.add(self.body, self.shape)
        self.pickupZone.Constrain(space, self.body)

