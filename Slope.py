import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
from collections import defaultdict
import math, sys, random
from Global import *
class Slope(object):
    """Accounts for tilted surfaces in 3D"""
    def __init__(self, name,context, vertices, angle, pos, direction):
        """angle in radians, direction is normalized vector """
        self.name = name
        self.context = context
        self.scale = SCALE
        self.vertices = [x * SCALE for x in vertices]
        self.angle = angle
        self.pos = [x * SCALE for x in pos] 
        self.body = pymunk.Body(1,1,pymunk.cp.CP_BODY_TYPE_STATIC)
        self.body.position = self.pos
        self.shape = pymunk.Poly(self.body, self.vertices)
        self.shape.sensor = True
        self.direction = direction
        self.context.objects[self.shape._get_shapeid()] = self
        self.shape.collision_type = collision_types[PLATFORM_NAME]

    def AddToSpace(self):
        self.context.space.add(self.body, self.shape)

    def GetForce(self, bot):
        return bot.body.mass * GRAV3D * math.sin(self.angle) * self.direction * SCALE


