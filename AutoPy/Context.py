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
        self.numRets = 0
        self.numBlueRets = 14 # number of rets total that can be received from blue feeder stations
        self.numRedRets = 14 # ^^ but for red
        self.count = 0
