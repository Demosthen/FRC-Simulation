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
    canPickup = False
    canScore = False
    rets = defaultdict(lambda:[])
    def __init__(self,name,  pos, color, width= 2.5, length=2.5, mass = 120, maxForce = 50, maxTorque = 50): #force in lbs
        self.name = name
        self.pPickUp = [] # probability of picking up retrievable
        self.tPickUp = [] # avg time spent picking up retrievable
        self.maxPickUp = dict()
        self.stPickUp = [] # std dev of pickup time?
        self.scores = [] # attainable scores in scorespots
        self.pScores = [] # probability of getting score at scorespots
        self.tScores = [] # avg time spent scoring at scorespot (seconds)
        self.stScores = [] # std dev of score time?
        self.width = width
        self.length = length
        self.mass=mass
        self.pos = pos
        self.hasCube = True
        self.score = 0
        self.force = maxForce
        self.torque = maxTorque
        self.color = color
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
        self.VisField = VisualField.VisualField("VisField",self.body, self.multiplier * 10, self.multiplier * 5)# make variables for vis field dims
        self.shape = pymunk.Poly(self.body,points)
        self.shape.elasticity = 0.95
        self.shape.friction = 1000
        self.shape.collision_type = self.name
        #self.shape.filter = pymunk.ShapeFilter(categories = 1)
        self.shape.color = pygame.color.THECOLORS[self.color]
        space.add(self.body, self.shape)
        self.VisField.AddToSpace(space, scale)
    def Randomize(self, numRet, numScore):#num types of retrievable not num of retrievables
        for i in range(numRet):
            pPickUp.append(random.uniform(0,1))
            tPickUp.append(random.uniform(0,1))
            stPickUp.append(random.uniform(0,1))
        for i in range(numScore):
            temp = random.uniform(0,1)
            pScores.append(round(temp) * temp)# >= 0.5 or = 0
            tScores.append(random.uniform(1,5))
            stScores.append(random.uniform(1,2))

    def GetScores(self, scoreList):
        scores = scoreList;
    def CheckInFront(self, space):#tested
        """check which shapes overlap w/ visual field, output shape[0] and contact point set[1]"""
        return space.shape_query(self.VisField.shape)
    def CheckState(self, space):# untested but prob works
        """check which shapes overlap with self"""
        return space.shape_query(self.shape)
    def PickUp(self, space, retrievable):# tested
        #TODO: 'remove' function in retrievable and set maxpickup
        # query space for pickup zone
        self.hasCube = True
        space.remove(retrievable.body, retrievable.shape)
        retrievable.body.position = self.body.position
        self.rets[retrievable.name] = retrievable
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

        



