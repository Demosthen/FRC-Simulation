import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import math, sys, random
import VisualField
class Bot(object):
    """Robot Object, 1"""
    
    def __init__(self, pos, color, width= 2.5, length=2.5, mass = 120, maxForce = 50, maxTorque = 50): #force in lbs
        self.pPickUp = [0] # probability of picking up retrievable
        self.tPickUp = [0] # avg time spent picking up retrievable
        self.stPickUp = [0] # std dev of pickup time?
        self.scores = [0] # attainable scores in scorespots
        self.pScores = [0] # probability of getting score at scorespots
        self.tScores = [0] # avg time spent scoring at scorespot (seconds)
        self.stScores = [0] # std dev of score time?
        self.width = width
        self.length = length
        self.mass=mass
        self.pos = pos
        self.hasCube = True
        self.score = 0
        self.force = maxForce
        self.torque = maxTorque
        self.color = color
        self.rets = []
        if color is "blue":
            self.multiplier = -1
        else:
            self.multiplier = 1
    def AddToSpace(self, scale, space):
        self.width *= scale
        self.length*=scale
        self.force *=scale
        points = [(-self.width/2, -self.length/2),(-self.width/2,self.length/2),(self.width/2,self.length/2),(self.width/2,-self.length/2)]
        self.inertia = pymunk.moment_for_poly(self.mass,points)
        self.body = pymunk.Body(self.mass, self.inertia)
        self.body.position = self.pos
        self.body.position *= scale
        self.VisField = VisualField.VisualField(self.body, self.multiplier * 10, self.multiplier * 5)# make variables for vis field dims
        self.shape = pymunk.Poly(self.body,points)
        self.shape.elasticity = 0.95
        self.shape.friction = 0.9
        self.shape.filter = pymunk.ShapeFilter(categories = 1)
        self.shape.color = pygame.color.THECOLORS[self.color]
        space.add(self.body, self.shape)
        self.VisField.AddToSpace(space, scale)
    def Randomize(self, numRet, numScore):#num types of retrievable not num of retrievables
        for i in range(1,numRet):
            pPickUp.append(random.uniform(0,1))
            tPickUp.append(random.uniform(0,1))
            stPickUp.append(random.uniform(0,1))
        for i in range(1, numScore):
            temp = random.uniform(0,1)
            pScores.append(round(temp) * temp)# >= 0.5 or = 0
            tScores.append(random.uniform(1,5))
            stScores.append(random.uniform(1,2))
    def GetScores(self, scoreList):
        scores = scoreList;
    def CheckInFront(self, space):#tested,
        """check which shapes overlap w/ visual field, output shape[0] and contact point set[1]"""
        return space.shape_query(self.VisField.shape)
    def PickUp(self, space, retrievable):# untested
        #do stuff
        self.hasCube = True
        space.remove(retrievable.body, retrievable.shape)
        retrievable.body.position = self.body.position
        self.rets.append(retrievable)
    def DropOff(self, space, retrievable, zone = None):# untested
        #do stuff
        self.hasCube = False
        self.rets.remove(retrievable)
        if zone !=None:
            if retrievable.name in zone.retKey:
                zone.GetRet(space, self)
        else:
            retrievable.body.position = self.body.position
            space.add(retrievable.body, retrievable.shape)
    def Penalize(self, space, zones):
        #do stuff
        hi
    def TurnLeft(self, proportion):#tested
        #TODO: Adjust torques
        self.body.apply_force_at_local_point((-proportion * self.torque,proportion * self.torque), (self.width/2, self.length/2))
    def TurnRight(self, proportion):#tested
        #TODO: Adjust torques
        self.body.apply_force_at_local_point((proportion * self.torque,-proportion * self.torque), (self.width/2, self.length/2))
    def Forward(self, proportion):#tested
        self.body.apply_force_at_local_point((proportion * self.force,0), (-self.width/2, 0))
    def BackWard(self, proportion):#tested
        self.body.apply_force_at_local_point((-proportion * self.force,0), (self.width/2, 0))
    def TakeAction(self, space, bots, zones, retrievables, obstacles):

        #insert neural net
        response = []

        



