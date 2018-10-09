import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
from collections import defaultdict
import math, sys, random
from SensorField import SensorField
from Retrievable import Retrievable
from Global import *
from Network import DISCOUNT
import multiprocessing as mp
class Bot(object):
    """Robot Object, 1"""
   
    staticInputSize = 6 # minimum size of input
    def __init__(self, name, context,  pos, color, manager, width= 2.5, length=2.5, mass = 120, maxForce = 400, maxTorque = 20000, maxSpeed = 30, maxAngSpeed = 1): #force in lbs
        self.name = name
        self.context = context
        self.pPickUp = dict.fromkeys(RET_NAMES) # probability of picking up retrievable
        self.tPickUp = dict.fromkeys(RET_NAMES) # avg time spent picking up retrievable
        self.maxPickUp = dict.fromkeys(RET_NAMES) # max # of rets in possession
        self.stPickUp = dict.fromkeys(RET_NAMES) # std dev of pickup time?
        self.scores = dict.fromkeys(SCORE_NAMES) # attainable scores in scorespots
        self.pScores = dict.fromkeys(SCORE_NAMES) # probability of getting score at scorespots
        self.tScores = dict.fromkeys(SCORE_NAMES) # avg time spent scoring at scorespot (seconds)
        self.stScores = dict.fromkeys(SCORE_NAMES) # std dev of score time?
        self.width = width * SCALE
        self.length = length * SCALE
        self.mass=mass
        self.pos = pos * SCALE
        self.maxSpeed = maxSpeed * SCALE
        self.maxAngSpeed = maxAngSpeed * SCALE
        self.angFriction = maxTorque * SCALE * 9
        self.maxForce = maxForce * SCALE
        self.force = Vec2d(0,0)
        self.maxTorque = maxTorque * SCALE
        self.torque = 0
        self.color = color
        self.scale = SCALE
        # create body
        points = [(-self.width/2, -self.length/2),(-self.width/2,self.length/2),(self.width/2,self.length/2),(self.width/2,-self.length/2)]
        self.inertia = pymunk.moment_for_poly(self.mass,points)
        self.body = pymunk.Body(self.mass, self.inertia)
        self.body.position = self.pos
        # setup control body
        self.control = pymunk.Body(pymunk.inf, pymunk.inf, body_type = pymunk.cp.CP_BODY_TYPE_KINEMATIC)
        self.control.position = self.body.position
        self.controlPivot = pymunk.PivotJoint(self.body, self.control,(0,0),(0,0))
        self.controlPivot.max_bias = 0
        self.controlPivot.max_force = 100 * self.maxForce
        self.controlGear = pymunk.GearJoint(self.body, self.control, 0, 1)
        self.controlGear.max_bias = 0
        self.controlGear.max_force = 250 * self.maxTorque
        #create shape
        self.shape = pymunk.Poly(self.body,points)
        self.shape.elasticity = 0.95
        self.shape.friction = 1000
        self.shape.color = pygame.color.THECOLORS[self.color]
        if color is "blue":
            self.score = self.context.blueScore
            self.multiplier = -1
        else:
            self.score = self.context.redScore
            self.multiplier = 1
        self.VisField = SensorField("VisField",self.context,self.body,  self.multiplier * 10, self.multiplier * 15, owner = self)# make variables for vis field dims
        self.RetField = SensorField("RetField", self.context, self.body, self.multiplier * 2, self.multiplier * 10, owner = self)
        self.shape.collision_type = collision_types[self.name]
        self.context.objects[self.shape._get_shapeid()] = self
        self.Randomize()
        self.damping = 1
        self.friction = maxForce * SCALE * 6
        self.canPickup = False
        self.canScore = False
        self.immobileTime = 0
        self.inputs = []
        self.RNNInputs = []
        self.logits = []
        self.actions = []
        self.teamScores =[]
        self.objectList = []
        self.rets = defaultdict(lambda:[])
        self.prev = 0 # team's score 1 second ago

    def KillLateralMvmt(self):
        self.control.velocity -= self.body.velocity.projection(Vec2d(math.cos(self.body.angle), math.sin(self.body.angle)).perpendicular())
    
    def ApplyFriction(self, friction):
        """insert force of friction"""
        force = -friction * self.body.velocity.normalized() * min(1.0, self.body.velocity.length * 2)
        self.body.apply_force_at_local_point(force,(0,0))

    def CapSpeed(self):
        self.control.velocity = self.control.velocity.normalized() * min(self.maxSpeed, self.control.velocity.length)

    def CapAngSpeed(self):
        self.control.angular_velocity = min(self.maxAngSpeed, abs(self.control.angular_velocity)) * ( 2 * int(self.control.angular_velocity > 0) - 1)

    def ControlVelUpdate(self, dt):
        accel = self.force / self.body.mass
        self.control.velocity += accel * dt
        fricDelta = dt * self.friction * self.control.velocity.normalized() / self.body.mass
        if (self.control.velocity.length > fricDelta.length ):
            self.control.velocity -= fricDelta
        else:    
            self.control.velocity = (0,0)
        angAccel = self.torque / self.body.moment
        self.control.angular_velocity += angAccel * dt
        angFricDelta = dt * self.angFriction /(self.body.moment)
        angFricDelta *= 2 * int(self.control.angular_velocity >= 0) - 1 # get sign
        if (self.control.angular_velocity - angFricDelta >= 0) == (self.control.angular_velocity >= 0):
            self.control.angular_velocity -= angFricDelta
        else: 
            self.control.angular_velocity = 0
        self.KillLateralMvmt()
        self.CapSpeed()
        self.CapAngSpeed()
        self.force = Vec2d(0,0)
        self.torque = 0

    def AddToSpace(self):
        if self.shape.space == None:
            self.context.space.add(self.body, self.shape, self.controlGear, self.controlPivot, self.control)
            self.VisField.AddToSpace()
            self.RetField.AddToSpace()

    def Randomize(self):
        """Set random parameters"""
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
            self.tScores[key] = random.uniform(1,4)
        for key, ret in self.stScores.items():
            self.stScores[key] = random.uniform(1,2)
        for key, ret in self.maxPickUp.items():
            self.maxPickUp[key] = 1 #in the case of powerup

    def CheckInFront(self):#tested
        """check which shapes overlap w/ visual field, output shape[0] and contact point set[1]"""
        return self.context.space.shape_query(self.VisField.shape)

    def CheckState(self):
        # untested but prob works
        """check which shapes overlap with self"""
        return self.context.space.shape_query(self.shape)

    def CheckInRetField(self):
        """check which shapes overlap with retfield"""
        return self.context.space.shape_query(self.RetField.shape)

    def ScoreZoneCheck(self):
        """checks if bot is in a scorezone of any kind"""
        shape_list = self.context.space.shape_query(self.shape)
        scoreZones = []
        for shape in shape_list:
            if not shape[0] == None and type(self.context.objects[shape[0]._get_shapeid()]).__name__ == 'ScoreZone' and self.context.objects[shape[0]._get_shapeid()].isScore :
                scoreZones.append(self.context.objects[shape[0]._get_shapeid()])
        return scoreZones

    def PickUpZoneCheck(self):
        """checks if bot is in a scorezone of any kind"""
        shape_list = self.context.space.shape_query(self.shape)
        scoreZones = []
        for shape in shape_list:
            if not shape[0] == None and type(self.context.objects[shape[0]._get_shapeid()]).__name__ == 'ScoreZone' and self.context.objects[shape[0]._get_shapeid()].isPickup :
                scoreZones.append(self.context.objects[shape[0]._get_shapeid()])
        return scoreZones

    def GetClosestRet(self, retName = CUBE_NAME):
        """returns a retrievable in the bot's retfield"""
        shape_list = self.context.space.shape_query(self.RetField.shape)
        for shape in shape_list:
            if shape == None:
                continue
            object = self.context.objects[shape[0]._get_shapeid()]
            if object.name == retName:
                return object
            #elif object.name == PICKUP_NAME or object.name == VAULT_NAME:
            #    return object
        return None

    def PickUp(self, retrievable):# tested
        if retrievable == None or not retrievable.name in RET_NAMES:
           return
        if len(self.rets[retrievable.name]) < self.maxPickUp[retrievable.name] and self.canPickup and self.immobileTime<=0:
            # make bot immobile for some time
            self.immobileTime = max(0, self.immobileTime + random.gauss(self.tPickUp[retrievable.name], self.stPickUp[retrievable.name]))
            # if bot is lucky it will pick up the thing
            if random.random() <= self.pPickUp[retrievable.name]:
                retrievable.Remove()
                retrievable.body.position = self.body.position
                retrievable.pickedUp = True
                self.rets[retrievable.name].append(retrievable)

    def ReceiveRet(self, retName):
        """Used in pickup zones"""
        if len(self.rets[retName]) < self.maxPickUp[retName] and self.canPickup:
            self.rets[retName].append(Retrievable(retName,self.context,self.body.position,3,1.083,1.083)) # replace dims with ret dims
            self.rets[retName][-1].pickedUp = True

    def DropOff(self,  retrievable, zone = None):# tested
        self.rets[retrievable.name].remove(retrievable)
        if zone != None and self.canScore and zone.retKey[retrievable.name] and random.random() <= self.pScores[zone.name] and self.immobileTime <=0:
             zone.GetRet(self, retrievable)
             self.immobileTime = max(random.gauss(self.tScores[zone.name], self.stScores[zone.name]), 0)
        else:
            retrievable.body.position = self.body.position
            retrievable.pickedUp = False
            retrievable.AddToSpace()

    retActKey = [PickUp,# 0
                 DropOff]# 1

    def TurnLeft(self, proportion):#tested
        if self.immobileTime <= 0:
            self.torque += proportion * self.maxTorque

    def TurnRight(self, proportion):#tested
        if self.immobileTime <= 0:
            self.torque -= proportion * self.maxTorque

    def Forward(self, proportion):#tested
        if self.immobileTime <= 0:
            direction = Vec2d(1,1)
            direction.angle = self.body.angle
            direction = direction.normalized()
            self.force += proportion * self.maxForce * direction * self.multiplier

    def Backward(self, proportion):#tested
        if self.immobileTime <= 0:
            direction = Vec2d(1,1)
            direction.angle = self.body.angle
            direction = -direction.normalized()
            self.force += proportion * self.maxForce * direction * self.multiplier

    def Brake(self, proportion = 1): #tested
        self.force = 0 
        self.torque = 0
        self.control.velocity = Vec2d(0,0)
        self.control.angular_velocity = 0

    mvmtKey = [Forward, # 0 
            Backward, # 1
            TurnRight, # 2
            TurnLeft, # 3
            Brake] # 4

    def GetInput(self):
        # get all objects in visual field
        shapes = self.CheckInFront()
        zones = self.CheckState()
        rets = self.CheckInRetField()
        # init with robot stats
        inputList = [self.mass, self.maxForce, self.maxTorque, self.maxSpeed, self.body.angular_velocity]
        inputList.extend(self.body.velocity)
        # add num of each ret held
        for list in self.rets:
            inputList.append(len(self.rets))
        self.objectList = []
        zoneList = []
        # add objects in view (no rets or zones)
        for shape, contacts in shapes:
            object = self.context.objects[shape._get_shapeid()]
            typ = type(object).__name__
            if typ == "Bot" or typ == "Obstacle":
                inputList.append(collision_types[object.name])
        for shape, contacts in rets:
            object = self.context.objects[shape._get_shapeid()]
            typ = type(object).__name__
            if typ == "Retrievable":
                self.objectList.append(object)
                inputList.append(collision_types[object.name])
        # in case bot wants to try to retrieve from a zone
        for name in RET_NAMES:
            inputList.append(collision_types[name])
        # add zones it is in (may need to be removed)
        #for shape, contacts in zones:
        #    zone = objects[shape._get_shapeid()]
        #    if type(object.__name__) == 'ScoreZone':
        #        zoneList.append(zone)
        #        inputList.append(collision_types[zone.name])
        return inputList

    def SaveInput(self):
        botInput = self.GetInput()
        origSize = len(botInput)
        while len(botInput) < INPUT_SIZE:
            botInput.append(0)
        self.inputs.append(botInput)
        return origSize

    def SaveAction(self, action):
        self.actions.append(action)

    def SaveLogits(self, logits):
        self.logits.append(logits)

    def SaveReward(self):# tested
        """save net score gain as reward"""
        self.teamScores.append(self.score.val - self.prev)
        self.prev = self.score.val

    def CalculateReward(self, timeStep):# tested
        minTime = math.ceil(timeStep)
        reward = 0
        for i in range(minTime, len(self.teamScores)):
            reward += pow(DISCOUNT, i - minTime) * self.teamScores[i]
        return reward + CORRECTION

    def AssignReward(self):# tested
        self.rewards = []
        for i in range(len(self.inputs)):
            self.rewards.append(self.CalculateReward(i / NUM_STEPS))

    def CleanUp(self):
        self.context.objects.pop(self.shape._get_shapeid())
        for list in self.rets.values():
            for ret in list:
                ret.CleanUp()
                del ret
        self.VisField.CleanUp()
        self.RetField.CleanUp()
        del self.VisField
        del self.RetField
        self.context.space.remove(self.shape,self.body,self.controlGear,self.controlPivot,self.control)