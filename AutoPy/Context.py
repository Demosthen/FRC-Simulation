from Global import *
import pymunk
class Context(object):
    def __init__(self):
        #Variables meant to be changed/accessed throughout program
        self.redScore = Int(0) 
        self.blueScore = Int(0)
        self.objects = defaultdict(lambda:None) # registry of all physical objects in game
        self.gameTime = 0 #seconds
        self.space = pymunk.space.Space()
