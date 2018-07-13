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
    def __init__(self, name, vertices, angle):
        self.name = name
        self.vertices = vertices
        self.angle = angle
        self.body = pymunk.Body(1,1,pymunk.cp.CP_BODY_TYPE_STATIC)
        self.shape = pymunk.Poly(self.body, vertices)
        objects[self.shape._get_shapeid()] = self
    def GetForce(self, bot):
        return bot.body.mass * grav3d * math.sin(angle)


