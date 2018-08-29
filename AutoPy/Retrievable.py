import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import math, sys, random
import copy
import ScoreZone
from Global import *
class Retrievable(object):
    """Retrievable object (Power Cube, whiffle ball, etc), 3"""
    def __init__(self, name, context, initPos, mass, width, length, radius = 0): # if num provided for radius, circle assumed
        self.name = name
        self.context = context
        self.mass = mass
        self.width = width * SCALE
        self.length = length * SCALE
        self.pos = initPos * SCALE
        self.radius = radius * SCALE
        self.scale = SCALE
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
        self.shape.color = pygame.color.THECOLORS["yellow"]
        self.pickupZone = ScoreZone.ScoreZone("Pickup",self.context,copy.deepcopy(self.pos),False, False, True,radius = 1)
        self.shape.collision_type = collision_types[self.name]
        self.context.objects[self.shape._get_shapeid()] = self

    def AddToSpace(self):
        self.pickupZone.AddToSpace()
        self.pickupZone.Constrain(self)
        self.context.space.add(self.body, self.shape)

    def Remove(self):
        self.pickupZone.inSpace = False
        self.context.space.remove(self.body,self.shape, self.pickupZone.body, self.pickupZone.shape, self.pickupZone.constraint)

    def CleanUp(self):
        self.context.objects.pop(self.shape._get_shapeid())
        if self.pickupZone.inSpace:
            self.pickupZone.CleanUp()
            self.context.space.remove(self.body, self.shape)
        del self.pickupZone