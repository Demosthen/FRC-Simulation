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
    def __init__(self, name, initPos,scale, mass, width, length, radius = 0): # if num provided for radius, circle assumed
        self.name = name
        self.mass = mass
        self.width = width * scale
        self.length = length * scale
        self.pos = initPos * scale
        self.radius = radius * scale
        self.scale = scale
        vertices = [(-self.width/2, -self.length/2),(-self.width/2,self.length/2),(self.width/2,self.length/2),(self.width/2,-self.length/2)]
        if self.radius > 0:
            self.inertia = pymunk.moment_for_circle(self.mass,self.radius,self.radius)
            self.body = pymunk.Body(self.mass,self.inertia)
            self.shape = pymunk.Circle(self.body,self.radius)
        else:
            self.inertia = pymunk.moment_for_poly(self.mass,vertices)
            self.body = pymunk.Body(self.mass, self.inertia)
            self.shape = pymunk.Poly(self.body, vertices)
        self.body.position = self.pos
        self.shape.elasticity = 0.95
        self.shape.friction = 0.9
        
        #self.shape.filter = pymunk.ShapeFilter(categories = 1)
        self.shape.color = pygame.color.THECOLORS["yellow"]
        self.pickupZone = ScoreZone.ScoreZone("Pickup",0,copy.deepcopy(self.pos),False, False, True,scale = scale,radius = 1)
    def AddToSpace(self, space, key):
        self.pickupZone.AddToSpace(space, key)
        self.shape.collision_type = key[self.name]
        space.add(self.body, self.shape)
        self.pickupZone.Constrain(space, self.body)
    def Remove(self, space):
        space.remove(self.body,self.shape)
        space.remove(self.pickupZone.body, self.pickupZone.shape)
