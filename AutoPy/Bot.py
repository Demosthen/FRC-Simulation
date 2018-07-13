import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
from collections import defaultdict
import math, sys, random
import VisualField
from Global import *
class Bot(object):
    """Robot Object, 1"""
    canPickup = False
    canScore = False
    rets = defaultdict(lambda:[])
    def __init__(self,name,  pos, color, score, width= 2.5, length=2.5, mass = 120, maxForce = 100, maxTorque = 50, maxSpeed = 15): #force in lbs
        self.name = name
        self.pPickUp = dict.fromkeys(RET_NAMES) # probability of picking up retrievable
        self.tPickUp = dict.fromkeys(RET_NAMES) # avg time spent picking up retrievable
        self.maxPickUp = dict.fromkeys(RET_NAMES) # max # of rets in possession
        self.stPickUp = dict.fromkeys(RET_NAMES) # std dev of pickup time?
        self.scores = dict.fromkeys(SCORE_NAMES) # attainable scores in scorespots
        self.pScores = dict.fromkeys(SCORE_NAMES) # probability of getting score at scorespots
        self.tScores = dict.fromkeys(SCORE_NAMES) # avg time spent scoring at scorespot (seconds)
        self.stScores = dict.fromkeys(SCORE_NAMES) # std dev of score time?
        self.width = width * scale
        self.length = length * scale
        self.mass=mass
        self.pos = pos * scale
        self.maxSpeed = maxSpeed * scale
        self.angFriction = 300
        self.hasCube = True
        self.score = score
        self.force = maxForce * scale
        self.torque = maxTorque * scale
        self.color = color
        self.scale = scale
        points = [(-self.width/2, -self.length/2),(-self.width/2,self.length/2),(self.width/2,self.length/2),(self.width/2,-self.length/2)]
        self.inertia = pymunk.moment_for_poly(self.mass,points)
        self.body = pymunk.Body(self.mass, self.inertia)
        self.body.position = self.pos
        #self.body._set_velocity_func()
        self.shape = pymunk.Poly(self.body,points)
        self.shape.elasticity = 0.95
        self.shape.friction = 1000
        self.shape.color = pygame.color.THECOLORS[self.color]
        if color is "blue":
            self.multiplier = -1
        else:
            self.multiplier = 1
        self.VisField = VisualField.VisualField("VisField",self.body,  self.multiplier * 10, self.multiplier * 5)# make variables for vis field dims
        self.shape.collision_type = collision_types[self.name]
        objects[self.shape._get_shapeid()] = self
        self.Randomize()
        self.damping = 1
        self.friction = maxForce * 300
        self.body.velocity_func = self.VelUpdate
    def KillLateralMvmt(self):
            self.body.velocity -= self.body.velocity.projection(Vec2d(math.cos(self.body.angle), math.sin(self.body.angle)).perpendicular())
    def ApplyFriction(self, friction):
        """insert force of friction"""
        force = -friction * self.body.velocity.normalized() * min(1.0, self.body.velocity.length * 2)
        self.body.apply_force_at_local_point(force,(0,0))
    def ApplyAngFriction(self, angFriction):
        if self.body.angular_velocity > 0:
            self.TurnRight(angFriction)
        elif self.body.angular_velocity < 0:
            self.TurnLeft(angFriction)
    def CapSpeed(self):
        self.body.velocity = self.body.velocity.normalized() * min(self.maxSpeed, self.body.velocity.length)
    def VelUpdate(self, Body, gravity, damping, dt):
        # kill lat mvmt to better simulate robot
        self.KillLateralMvmt()
        self.CapSpeed()
        # update with custom damping value
        Body.update_velocity(Body, gravity,self.damping, dt)
        self.ApplyAngFriction(self.angFriction)
        self.ApplyFriction(self.friction)
    def AddToSpace(self, space):
        if self.shape.space == None:
            space.add(self.body, self.shape)
            self.VisField.AddToSpace(space)
    def Randomize(self):
        for key, ret in self.pPickUp.items():
            self.pPickUp[key] = random.uniform(0,1)
        for key, ret in self.tPickUp.items():
            self.tPickUp[key] = random.uniform(1,3)
        for key, ret in self.stPickUp.items():
            self.stPickUp[key] = random.uniform(0,1)
        for key, ret in self.pScores.items():
            temp = random.uniform(0,1)
            self.pScores[key] = round(temp) * temp# >=0.5 or = 0
        for key, ret in self.tScores.items():
            self.tScores[key] = random.uniform(1,5)
        for key, ret in self.stScores.items():
            self.stScores[key] = random.uniform(1,2)
    def GetScores(self, scoreDict):
        scores = scoreDict
    def CheckInFront(self, space):#tested
        """check which shapes overlap w/ visual field, output shape[0] and contact point set[1]"""
        return space.shape_query(self.VisField.shape)
    def CheckState(self, space):# untested but prob works
        """check which shapes overlap with self"""
        return space.shape_query(self.shape)
    def GetClosestRet(self, space):
        shape_list = space.shape_query(self.shape)
        for shape in shape_list:
            if not shape == None and objects[shape[0]._get_shapeid()].name == CUBE_NAME:
                return objects[shape[0]._get_shapeid()]
            elif (not shape == None) and (objects[shape[0]._get_shapeid()].name == PICKUP_NAME or objects[shape[0]._get_shapeid()].name == VAULT_NAME):
                return objects[shape[0]._get_shapeid()].GiveRet( space, self, CUBE_NAME)
        return None
    def ScoreZoneCheck(self,space):
        shape_list = space.shape_query(self.shape)
        scoreZones = []
        for shape in shape_list:
            if not shape[0] == None and type(objects[shape[0]._get_shapeid()]).__name__ == 'ScoreZone' and objects[shape[0]._get_shapeid()].isScore:
                scoreZones.append(objects[shape[0]._get_shapeid()])
        return scoreZones
    def PickUp(self, space, retrievable):# tested
        #TODO: set maxpickup
        # query space for pickup zone
        if self.canPickup:
            self.hasCube = True
            retrievable.Remove(space)
            retrievable.body.position = self.body.position
            self.rets[retrievable.name].append(retrievable)
    def DropOff(self, space, retrievable, zone = None):# untested
        #do stuff
        self.hasCube = False
        self.rets[retrievable.name].remove(retrievable)
        if zone !=None and self.canScore and zone.retKey[retrievable.name]:
             zone.GetRet(space, self, retrievable)
        else:
            retrievable.body.position = self.body.position
            retrievable.AddToSpace(space)
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
    def Backward(self, proportion):#tested
        self.body.apply_force_at_local_point((-proportion * self.force,0), (self.width/2, 0))
    def TakeAction(self, space, bots, zones, retrievables, obstacles):

        #insert neural net
        response = []

        



