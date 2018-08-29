from Global import *
import multiprocessing as mp
currentProcess = mp.current_process().name
if currentProcess == SIM_PROC_NAME:
    import pygame
    from pygame.locals import *
    from pygame.color import *
    from pygame.key import *
    import pymunk
    import pymunk.pygame_util
    from pymunk import Vec2d
    from Bot import Bot
    from ScoreZone import ScoreZone
    from Retrievable import Retrievable
    from Obstacle import Obstacle
    from Slope import Slope
    from Field import Field
from collections import defaultdict
import math, sys, random
from Int import Int
import copy
import time

from Network import Network as nw
import tensorflow as tf
import numpy as np
from Context import Context
from CollisionHandlers import *
def SimFnWrapper(network,pipe):
    SimFn(network,pipe)

if __name__ == "__main__":
    simProcs = []
    simPipes = []
    data = []
    
    network = nw()
    placeholder = tf.placeholder(tf.float32, [None,INPUT_SIZE])
    feedForward = network.feedForward(placeholder)
    
    for i in range(NUM_SIMS):
        simPipes.append(mp.Pipe())
        simProcs.append(mp.Process(target = SimFnWrapper, name = SIM_PROC_NAME, args = [network,simPipes[i][1]], daemon = False))
        simProcs[i].start()
    for j in range(NUM_GAMES):
        for i in range(NUM_SIMS):
            simPipes[i][0].send(True)
        print("done sending")
        for i in range(NUM_SIMS):
            print("starting receipt")
            datum = simPipes[i][0].recv()
            data.append(datum)
        print(len(data[0][0][0]))
    print("done simulating games")
    for i in range(NUM_SIMS):
        simProcs[i].join()

def getAction(network, inputConn):
    sess = tf.Session()
    placeholder = tf.placeholder(tf.float32, [None,INPUT_SIZE])
    feedForward = network.feedForward(placeholder)
    sess.run(tf.global_variables_initializer())
    while True:
        input = inputConn.recv()
        inputConn.send(feedForward.eval(feed_dict = {placeholder: input}, session = sess)[0])

def SimFn(network,pipe):
    sess = tf.Session()
    placeholder = tf.placeholder(tf.float32, [None,INPUT_SIZE])
    feedForward = network.feedForward(placeholder)
    sess.run(tf.global_variables_initializer())
    
    
    #Lengths are in ft and masses are in lbs
    def getColors():
        """return scale and switch colors in that order"""
        switch = ["red", "blue"]
        if random.random() >= 0.5:
            switch[0], switch[1] = switch[1], switch[0]
        scale = ["red", "blue"]
        if random.random() >= 0.5:
            scale[0], scale[1] = scale[1], scale[0]
        return scale, switch

    def AddObjects(list):
        for elem in list:
            context.objects[elem.shape._get_shapeid()] = elem

    def scaleScore(scaleZones):#call every second pls
        if scaleZones[int(scaleZones[0].numRet < scaleZones[1].numRet)].color == "red":
            context.redScore.val += SCALE_POINTS * int(not scaleZones[0].numRet == scaleZones[1].numRet)
        else:
            context.blueScore.val += SCALE_POINTS * int(not scaleZones[0].numRet == scaleZones[1].numRet)

    def switchScore(switchZones):#call every second pls
        if switchZones[int(switchZones[0].numRet < switchZones[1].numRet)].color == "red":
            context.redScore.val += SCALE_POINTS * int(not switchZones[0].numRet == switchZones[1].numRet)
        else:
            context.blueScore.val += SCALE_POINTS * int(not switchZones[0].numRet == switchZones[1].numRet)

        if switchZones[int(switchZones[2].numRet < switchZones[3].numRet)].color == "red":
            context.redScore.val += SCALE_POINTS * int(not switchZones[2].numRet == switchZones[3].numRet)
        else:
            context.blueScore.val += SCALE_POINTS * int(not switchZones[2].numRet == switchZones[3].numRet)

    def vaultScore(vaultZones):# per cube
        redIndex = int(vaultZones[1].color == "red") 
        context.redScore.val += VAULT_POINTS * vaultZones[redIndex].numRet
        context.blueScore.val += VAULT_POINTS * vaultZones[1-redIndex].numRet

    if  currentProcess == SIM_PROC_NAME:
        context = Context()
        manager = mp.Manager()
        bots = []
        vaults = []
        scales = []
        switches = []
        scaleBarriers = []
        scalePenalties = []
        switchBarriers = []
        cubes = []
        cubePickup = []
        platforms = []
        scaleColor, switchColor = getColors()

        def MakeBots():
            bots.append(Bot(BOT_NAME,context,pos = BOT_START_POS[0], color = "red", manager = manager))
            bots.append(Bot(BOT_NAME,context,pos = BOT_START_POS[1], color = "red", manager = manager))
            bots.append(Bot(BOT_NAME,context,pos = BOT_START_POS[2], color = "red", manager = manager))
            bots.append(Bot(BOT_NAME,context,pos = BOT_START_POS[3], color = "blue", manager = manager))
            bots.append(Bot(BOT_NAME,context,pos = BOT_START_POS[4], color = "blue", manager = manager))
            bots.append(Bot(BOT_NAME,context,pos = BOT_START_POS[5], color = "blue", manager = manager))

        def MakeVaults():
            vaults.append(ScoreZone(VAULT_NAME,context,Vec2d((2.5,17.5)), True, False, True,"red", 3,4,retKey = VAULT_RETKEY))
            vaults.append(ScoreZone(VAULT_NAME,context,Vec2d((FIELD_LENGTH-0.5,FIELD_WIDTH-16.5)), True, False, True,"blue", 3,4,retKey = VAULT_RETKEY))
    
        def MakeSwitches():
            switches.append(ScoreZone(SWITCH_NAME,context,Vec2d((15,21)),True, False, False,switchColor[0], radius = 3, retKey = SWITCH_RETKEY))
            switches.append(ScoreZone(SWITCH_NAME,context,Vec2d((15,8)),True, False, False,switchColor[1],radius = 3, retKey = SWITCH_RETKEY))
            switches.append(ScoreZone(SWITCH_NAME,context,Vec2d((41,21)),True, False, False,switchColor[0],radius = 3, retKey = SWITCH_RETKEY))
            switches.append(ScoreZone(SWITCH_NAME,context,Vec2d((41,8)),True, False, False,switchColor[1],radius = 3, retKey = SWITCH_RETKEY))

        def MakeScales():
            scales.append(ScoreZone(SCALE_NAME,context,Vec2d((28,20)),True,False,False,scaleColor[0],radius = 3.5, retKey = SCALE_RETKEY))
            scales.append(ScoreZone(SCALE_NAME,context,Vec2d((28,9)),True, False, False,scaleColor[1],radius = 3.5, retKey = SCALE_RETKEY))

        def MakeScaleBarriers():
            """physical scale obstacle"""
            scaleBarriers.append(Obstacle(OBSTACLE_NAME,context,Vec2d((28,14.5)), 1.42,10.79))

        def MakeScalePenalties():
            """space under scales (penalized bc unpredictable)"""
            scalePenalties.append(ScoreZone(SCALE_PENALTY_NAME,context,Vec2d((28,20)),False, True, False,scaleColor[0],4,3))
            scalePenalties.append(ScoreZone(SCALE_PENALTY_NAME,context,Vec2d((28,9)),False, True, False,scaleColor[1],4,3))
    
        def MakeSwitchBarriers():
            """physical switch obstacle"""
            switchBarriers.append(Obstacle(OBSTACLE_NAME,context,Vec2d((15,14.5)),3,12.75))
            switchBarriers.append(Obstacle(OBSTACLE_NAME,context,Vec2d((41,14.5)),3,12.75))

        def MakeCubes():
            # add retrievable cubes
            for i in range(10):
                cubes.append(Retrievable(CUBE_NAME,context, Vec2d(( random.uniform(-1,1)+12.125,14.5 + random.uniform(-1,1))),3,1.083,1.083)) # form group to simulate pyramid
                cubes.append(Retrievable(CUBE_NAME,context, Vec2d(( random.uniform(-1,1)+FIELD_LENGTH-11.125,14.5 + random.uniform(-1,1))),3,1.083,1.083))

            for i in range(6):
                cubes.append(Retrievable(CUBE_NAME,context, Vec2d((16.875,20.354 - i * 2.342)), 3,1.083,1.083))
                cubes.append(Retrievable(CUBE_NAME,context, Vec2d((FIELD_LENGTH-14.875,20.354- i * 2.342)), 3,1.083,1.083))

        def MakeCubePickupZones():
            """areas where you pick up cubes"""
            cubePickup.append(ScoreZone(PICKUP_NAME,context, Vec2d((2,FIELD_LENGTH/2)),False, False, True,"blue", radius = 1.5))
            cubePickup.append(ScoreZone(PICKUP_NAME,context, Vec2d((2,2)), False, False, True,"blue", radius = 1.5))
            cubePickup.append(ScoreZone(PICKUP_NAME,context, Vec2d((FIELD_LENGTH,FIELD_LENGTH/2)),False, False, True,"red", radius = 1.5))
            cubePickup.append(ScoreZone(PICKUP_NAME,context, Vec2d((FIELD_LENGTH,2)), False, False, True,"red", radius = 1.5))

        def MakePlatforms():
            top = [8.66517,4.4893, 3.4375]
            botm = [10.76892,3.4375, 4.4893]
            length = [1.06175,1.06175, 1.06175]
            vertices = [(Vec2d(-length[0], -botm[0]), Vec2d(-length[0], botm[0]), Vec2d(length[0], top[0]), Vec2d(length[0], -top[0])),
                        (Vec2d(botm[1]-top[1], -length[1]), Vec2d(-top[1], length[1]), Vec2d(top[1], length[1]), Vec2d(top[1], -length[1])),
                        (Vec2d(-botm[2], -length[2]), Vec2d(top[2]-botm[2], length[2]), Vec2d(botm[2], length[2]), Vec2d(botm[2], -length[2]))]
            otherverts = copy.deepcopy(vertices)
            # mirror platform to other side of scale
            for list in otherverts:
                for vertex in list:
                    vertex[0] = -vertex[0]
                vertices.append(list)
            # correct vertices
            for list in vertices:
                for vertex in list:
                    vertex /= 2
            platforms.append(Slope(PLATFORM_NAME,context, vertices[0],0.271593,(23.3111, 14.5), Vec2d(-1,0)))
            platforms.append(Slope(PLATFORM_NAME,context, vertices[1], 0.271593, (25.042, 19.375), Vec2d(0,1)))
            platforms.append(Slope(PLATFORM_NAME,context, vertices[2], 0.271593, (25.042, 9.6273), Vec2d(0,-1)))
            platforms.append(Slope(PLATFORM_NAME,context, vertices[3],0.271593,(FIELD_LENGTH - 21.3111, 14.5), Vec2d(1,0)))
            platforms.append(Slope(PLATFORM_NAME,context, vertices[4], 0.271593, (FIELD_LENGTH - 23.042, 19.375), Vec2d(0,1)))
            platforms.append(Slope(PLATFORM_NAME,context, vertices[5], 0.271593, (FIELD_LENGTH - 23.042, 9.6273), Vec2d(0,-1)))

        def Reset():
            context.redScore.val = 0
            context.blueScore.val = 0
            context.gameTime = 0
            for bot in bots:
                bot.CleanUp()
            for cube in cubes:
                cube.CleanUp()
            bots.clear()
            cubes.clear()
            MakeBots()
            MakeCubes()
            for switch in switches:
                switch.numRet = 0
            for scale in scales:
                scale.numRet = 0
            for vault in vaults:
                vault.numRet = 0
            for bot in bots:
                bot.AddToSpace()
            for cube in cubes:
                cube.AddToSpace()
        ### Physics stuff
        context.space.gravity = (0.0, 0.0)
        context.space.damping = 0.05
        penaltyCounter = 0
        canForce = False
        canLevitate = False
        canBoost = False
        static_body = context.space.static_body

        #add field walls
        field = Field(context,static_body)

        MakeBots()
        MakeVaults()
        MakeScales()
        MakeScaleBarriers()
        MakeScalePenalties()
        MakeSwitches()
        MakeSwitchBarriers()
        MakeCubes()
        MakeCubePickupZones()
        MakePlatforms()

        #add everything to space
        for key, zone in context.objects.items():
                zone.AddToSpace()

        #set collision handlers, pass objects registry as data so they can trace shapes back to objects
        botSwitch = context.space.add_collision_handler(collision_types[BOT_NAME], collision_types[SWITCH_NAME])
        botSwitch.data[0] = context
        botSwitch.pre_solve = beginBotScore
        botSwitch.separate = endBotScore

        botScale = context.space.add_collision_handler(collision_types[BOT_NAME], collision_types[SCALE_NAME])
        botScale.data[0] = context
        botScale.pre_solve = beginBotScore
        botScale.separate = endBotScore

        botVault = context.space.add_collision_handler(collision_types[BOT_NAME], collision_types[VAULT_NAME])
        botVault.data[0] = context
        botVault.pre_solve  = beginBotVault
        botVault.separate = endBotVault

        botBot = context.space.add_collision_handler(collision_types[BOT_NAME], collision_types[BOT_NAME])
        botBot.data[0] = context
        botBot.pre_solve = duringBotBot

        botPickup = context.space.add_collision_handler(collision_types[BOT_NAME], collision_types[PICKUP_NAME])
        botPickup.data[0] = context
        botPickup.pre_solve  = beginBotPickup
        botPickup.separate = endBotPickup

        botPlatform = context.space.add_collision_handler(collision_types[BOT_NAME], collision_types[PLATFORM_NAME])
        botPlatform.data[0] = context
        botPlatform.pre_solve = duringBotPlatform

        botScalePenalty = context.space.add_collision_handler(collision_types[BOT_NAME], collision_types[SCALE_PENALTY_NAME])
        botScalePenalty.data[0] = context
        botScalePenalty.begin = beginBotScalePenalty

        forwardFlag = False
        backFlag = False
        rightFlag = False
        leftFlag = False
        pygame.init()
        screen = pygame.display.set_mode((1200, 600))
        draw_options = pymunk.pygame_util.DrawOptions(screen)
        clock = pygame.time.Clock()
        running = True
        inputs = []
        #6 processes to simulate decisions of 6 robots
        pipes = []# 2nd index 0 = parentconn, 1 = childconn
        nnProcs = []
        #for i in range(NUM_BOTS):
            #pipes.append(mp.Pipe())
            #nnProcs.append(mp.Process(target = getAction,name = NN_PROC_NAME, args = [network, pipes[i][1]], daemon = True))
            #nnProcs[i].start()
        print("done with setup")
        #main loop
        while(True):
            cue = pipe.recv()
            print("starting simulation")
            print(context.gameTime)
            while running and context.gameTime < GAME_DURATION:
                for event in pygame.event.get():
                    # debug input
                    if event.type == QUIT:
                        running = False
                    elif event.type == KEYDOWN and event.key == K_ESCAPE:
                        running = False
                    elif event.type == KEYDOWN and event.key == K_e:
                        if len(bots[1].rets[CUBE_NAME]) > 0:
                            zones = bots[1].ScoreZoneCheck()
                            if len(zones) > 0:
                                bots[1].DropOff(bots[1].rets[CUBE_NAME][0], zones[0])
                            else:
                                bots[1].DropOff(bots[1].rets[CUBE_NAME][0])
                    elif event.type == KEYDOWN and event.key == K_w:
                        forwardFlag = True
                    elif event.type == KEYUP and event.key == K_w:
                        forwardFlag = False
                    elif event.type == KEYDOWN and event.key == K_s:
                        backFlag = True
                    elif event.type == KEYUP and event.key == K_s:
                        backFlag = False
                    elif event.type == KEYDOWN and event.key == K_d:
                        rightFlag = True
                    elif event.type == KEYUP and event.key == K_d:
                        rightFlag = False
                    elif event.type == KEYDOWN and event.key == K_a:
                        leftFlag = True
                    elif event.type == KEYUP and event.key == K_a:
                        leftFlag = False
                    elif event.type == KEYDOWN and event.key == K_q:
                        bots[1].PickUp(bots[1].GetClosestRet(CUBE_NAME))
                    elif event.type == KEYDOWN and event.key == K_f:
                        vaultScore(vaults)
                    elif event.type == KEYDOWN and event.key == K_g:
                        bots[1].Brake()
                if forwardFlag:
                    bots[1].Forward(10)
                if rightFlag:
                    bots[1].TurnRight(10)
                if leftFlag:
                    bots[1].TurnLeft(10)
                if backFlag:
                    bots[1].Backward(10)
                if MODE == "DRAW":
                    ### Clear screen
                    screen.fill(THECOLORS["white"])

                    ### Draw stuff
                    context.space.debug_draw(draw_options)
                ## Update physics, move forward 1/STEP_SIZE second
                dt = 1.0/NUM_STEPS
                for x in range(1):
                    for bot in bots:
                        bot.ControlVelUpdate(dt)
                    context.space.step(dt)
                    context.gameTime += dt
                    for bot in bots:
                        bot.immobileTime -= dt
                

                #for i in range(NUM_BOTS):
                    #pipes[i][0].send(bots[i].inputs[-15:])
                    #feedForward.eval(feed_dict = {placeholder: input}, session = sess)[0]
                if(int(context.gameTime/dt) % 6 == 0):
                    #save input for training neural net later
                    origSize = []
                    for bot in bots:
                        origSize.append( bot.SaveInput() )
                    for i in range(NUM_BOTS):
                        #batchOutput = pipes[i][0].recv()
                        batchOutput = feedForward.eval(feed_dict = {placeholder: bots[i].inputs[-15:]}, session = sess)[0]
                        output = batchOutput[0]
                        mvmt = output[:5] # isolate mvmt outputs
                        bots[i].mvmtKey[np.argmax(mvmt,0)](bots[i],10) # execute appropriate movement based on nn output
                        numTypes = len(bots[i].rets)
                        if(numTypes > 1):
                            maxRet = np.amax(output[5:5+numTypes])
                            dropIndex = np.argmax(output[5:5+numTypes]) + 5
                        else:
                            maxRet = output[5]
                            dropIndex = 5
                        if maxRet < 0.5:
                            dropIndex = -1
                        else:
                            rets = bots[i].rets[np.argmax(output[5:5+numTypes])]

                            zones = bots[i].ScoreZoneCheck()
                        
                            if len(zones) > 0 and len(rets) > 0:
                                # if there is a zone nearby, drop it there
                                bots[i].DropOff(rets[0], bots[i].ScoreZoneCheck()[0])
                            elif len(bots[i].rets[j]) > 0:
                                bots[i].DropOff(rets[0])
                        numAhead = origSize[i] - 5 - numTypes # get number of shapes ahead of bot
                        pickUpIndex = -1
                        for k in range(numAhead):
                            if output[5 + numTypes + k] > 0.5:# smth wrong here pls fix later
                                bots[i].PickUp(bots[i].GetClosestRet())
                                pickUpIndex = 5 + numTypes + k
                                break
                        action = []
                        action.extend(mvmt)
                        action.append(dropIndex)
                        action.append(pickUpIndex)
                        bots[i].SaveAction(action)
        
                #stuff done every second
                if not int(context.gameTime - dt) == int(context.gameTime):
                    #update scale and switch scores
                    scaleScore( scales)
                    switchScore( switches)
                    print(context.gameTime)
                    #save scores
                    for bot in bots:
                        bot.SaveReward()
            if MODE == "DRAW":
            ### Flip screen
                pygame.display.flip()
                clock.tick()
                pygame.display.set_caption("fps: " + str(clock.get_fps()) + " red: " + str(context.redScore.val) + " blue: " + str(context.blueScore.val))
            inputs = []
            actions = []
            rewards = []
            print("sending data")
            for bot in bots:
                bot.AssignReward()
                inputs.append(bot.inputs)
                actions.append(bot.actions)
                rewards.append(bot.rewards)
            pipe.send([inputs, actions, rewards])
            print("sim done")
            Reset()
    #NOTES:
    #test
    #better to undestimate visual field bc convnet can mislabel at edges
    #TODO:
    #will give key error if you try to remove a shape/body while its collision is being handled
    #start training! yayyyyy
    #rename ScoreZone to Zone object later