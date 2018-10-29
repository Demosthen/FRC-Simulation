from Global import *
import multiprocessing as mp
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
import runpy
import Network as nw
import tensorflow as tf
import numpy as np
from Context import Context
from CollisionHandlers import *
import InfoWindow

currentProcess = mp.current_process().name

def SimFn(pipe):
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
        change = SCALE_POINTS * int(not scaleZones[0].numRet == scaleZones[1].numRet)
        if scaleZones[int(scaleZones[0].numRet < scaleZones[1].numRet)].color == "red":
            context.redScore.val += change
        else:
            context.blueScore.val += change
        return change

    def switchScore(switchZones):#call every second pls
        change1 = SCALE_POINTS * int(not switchZones[0].numRet == switchZones[1].numRet)
        if switchZones[int(switchZones[0].numRet < switchZones[1].numRet)].color == "red":
            context.redScore.val += change1
        else:
            context.blueScore.val += change1

        change2 = SCALE_POINTS * int(not switchZones[2].numRet == switchZones[3].numRet)
        if switchZones[int(switchZones[2].numRet < switchZones[3].numRet)].color == "red":
            context.redScore.val += change2
        else:
            context.blueScore.val += change2
        return change1, change2

    def vaultScore(vaultZones, prevRed, prevBlue):# per cube
        redIndex = int(vaultZones[1].color == "red") 
        context.redScore.val += VAULT_POINTS * (vaultZones[redIndex].numRet - prevRed)
        context.blueScore.val += VAULT_POINTS * (vaultZones[1-redIndex].numRet - prevBlue)
        return vaultZones[redIndex].numRet , vaultZones[1-redIndex].numRet

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
        context.scaleColor, context.switchColor = getColors()
        if MODE == "DRAW":
            infoPipe = mp.Pipe()
            info = mp.Process(target = InfoWindow.run, args = [infoPipe[1]], daemon = True)
            info.start()

        def MakeBots():
            for i in range(NUM_BOTS):
                if i < NUM_BOTS/2:
                    bots.append(Bot(BOT_NAME,context,pos = BOT_START_POS[i], color = "red", manager = manager))
                else:
                    bots.append(Bot(BOT_NAME,context,pos = BOT_START_POS[i], color = "blue", manager = manager))
                bots[-1].canPickup = True
                bots[-1].ReceiveRet(CUBE_NAME)
                bots[-1].canPickup = False

        def MakeVaults():
            vaults.append(ScoreZone(VAULT_NAME,context,Vec2d((2.5,17.5)), True, False, False,"red", 3,4,retKey = VAULT_RETKEY))
            vaults.append(ScoreZone(VAULT_NAME,context,Vec2d((FIELD_LENGTH-0.5,FIELD_WIDTH-16.5)), True, False, False,"blue", 3,4,retKey = VAULT_RETKEY))

        def MakeSwitches():
            switches.append(ScoreZone(SWITCH_NAME,context,Vec2d((15,21)),True, False, False,context.switchColor[0], radius = 3, retKey = SWITCH_RETKEY))
            switches.append(ScoreZone(SWITCH_NAME,context,Vec2d((15,8)),True, False, False,context.switchColor[1],radius = 3, retKey = SWITCH_RETKEY))
            switches.append(ScoreZone(SWITCH_NAME,context,Vec2d((41,21)),True, False, False,context.switchColor[0],radius = 3, retKey = SWITCH_RETKEY))
            switches.append(ScoreZone(SWITCH_NAME,context,Vec2d((41,8)),True, False, False,context.switchColor[1],radius = 3, retKey = SWITCH_RETKEY))

        def MakeScales():
            scales.append(ScoreZone(SCALE_NAME,context,Vec2d((28,20)),True,False,False,context.scaleColor[0],radius = 3.5, retKey = SCALE_RETKEY))
            scales.append(ScoreZone(SCALE_NAME,context,Vec2d((28,9)),True, False, False,context.scaleColor[1],radius = 3.5, retKey = SCALE_RETKEY))

        def MakeScaleBarriers():
            """physical scale obstacle"""
            scaleBarriers.append(Obstacle(OBSTACLE_NAME,context,Vec2d((28,14.5)), 1.42,10.79))

        def MakeScalePenalties():
            """space under scales (penalized bc unpredictable)"""
            scalePenalties.append(ScoreZone(SCALE_PENALTY_NAME,context,Vec2d((28,20)),False, True, False,context.scaleColor[0],4,3))
            scalePenalties.append(ScoreZone(SCALE_PENALTY_NAME,context,Vec2d((28,9)),False, True, False,context.scaleColor[1],4,3))
    
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
            cubePickup.append(ScoreZone(PICKUP_NAME,context, Vec2d((2,FIELD_LENGTH/2)),False, False, True,"blue", radius = 1.5, retKey = PICKUP_RETKEY))
            cubePickup.append(ScoreZone(PICKUP_NAME,context, Vec2d((2,2)), False, False, True,"blue", radius = 1.5, retKey = PICKUP_RETKEY))
            cubePickup.append(ScoreZone(PICKUP_NAME,context, Vec2d((FIELD_LENGTH,FIELD_LENGTH/2)),False, False, True,"red", radius = 1.5, retKey = PICKUP_RETKEY))
            cubePickup.append(ScoreZone(PICKUP_NAME,context, Vec2d((FIELD_LENGTH,2)), False, False, True,"red", radius = 1.5, retKey = PICKUP_RETKEY))

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
            context.numBlueRets = 14
            context.numRedRets = 14

            for shape in context.space.shapes:
                object = context.objects[shape._get_shapeid()]
                if object != None and (object.name in TO_RESET):
                    object.CleanUp()
                    del object
            bots.clear()
            cubes.clear()
            switches.clear()
            scales.clear()
            context.numRets = 0
            MakeBots()
            MakeCubes()
            context.scaleColor, context.switchColor = getColors()
            MakeSwitches()
            MakeScales()
            for vault in vaults:
                vault.numRet = 0
                vault.CleanOut()
            for bot in bots:
                bot.AddToSpace()
            for cube in cubes:
                cube.AddToSpace()
            for scale in scales:
                scale.AddToSpace()
            for switch in switches:
                switch.AddToSpace()

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
        for key, object in context.objects.items():
                object.AddToSpace()

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
        FieldRets = []
        for retName in RET_NAMES:
            FieldRets.append(context.space.add_collision_handler(collision_types[RETFIELD_NAME], collision_types[retName]))
            FieldRets[-1].data[0] = context
            FieldRets[-1].pre_solve = beginFieldRet
            FieldRets[-1].separate = endFieldRet
        forwardFlag = False
        backFlag = False
        rightFlag = False
        leftFlag = False
        dropFlag = False
        pickupFlag = False
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
        print("done with setup", "w")
        inFile = open("inputs.txt", "w")
        outFile = open("outputs.txt", "w")
        rewardFile = open("rewards.txt", "w")
        #main loop
        while(True):
            cue = pipe.recv()
            if context.count > 0:
                nw.saver.restore(nw.sess, nw.SAVE_PATH)
            context.count += 1 #number of simulations done
            prevRed = 0
            prevBlue = 0
            print("starting simulation")
            print(context.gameTime)
            while running and context.gameTime < GAME_DURATION:
                dropFlag = False
                pickupFlag = False
                for event in pygame.event.get():
                    # debug input
                    if event.type == QUIT:
                        running = False
                    elif event.type == KEYDOWN and event.key == K_ESCAPE:
                        running = False
                    elif event.type == KEYDOWN and event.key == K_e:
                        dropFlag = True
                        bots[1].DropOffNearest(CUBE_NAME)
                        #if len(bots[1].rets[CUBE_NAME]) > 0:
                        #    zones = bots[1].ScoreZoneCheck()
                        #    if len(zones) > 0:
                        #        bots[1].DropOff(bots[1].rets[CUBE_NAME][0], zones[0])
                        #    else:
                         #       bots[1].DropOff(bots[1].rets[CUBE_NAME][0])
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
                        pickupFlag = True
                        bots[1].PickUpNearest(CUBE_NAME)
                        #zones = bots[1].PickUpZoneCheck()
                        #if len(zones)>0:
                        #    zones[0].GiveRet(bots[1], CUBE_NAME)
                        #else:
                        #    bots[1].PickUp(bots[1].GetClosestRet())
                    elif event.type == KEYDOWN and event.key == K_f:
                        vaultScore(vaults, prevRed, prevBlue)
                    elif event.type == KEYDOWN and event.key == K_g:
                        bots[1].Brake()
                if forwardFlag:
                    bots[1].Forward(SCALE)
                if rightFlag:
                    bots[1].TurnRight(SCALE)
                if leftFlag:
                    bots[1].TurnLeft(SCALE)
                if backFlag:
                    bots[1].Backward(SCALE)
                if MODE == "DRAW":
                    ### Clear screen
                    screen.fill(THECOLORS["white"])
                    ### Draw stuff
                    context.space.debug_draw(draw_options)
                ## Update physics, move forward 1/NUM_STEPS second
                dt = 1.0/NUM_STEPS
                for x in range(1):
                    for bot in bots:
                        bot.ControlVelUpdate(dt)
                    context.space.step(dt)
                    context.gameTime += dt
                    for bot in bots:
                        bot.immobileTime -= dt
                
                latestIdx = -1
                latestValue = -1
                #for i in range(NUM_BOTS):
                    #pipes[i][0].send(bots[i].inputs[-15:])
                    #feedForward.eval(feed_dict = {placeholder: input}, session = sess)[0]
                if(int(context.gameTime/dt) % ACTION_TIMING == 0):#get bot's action
                    
                    infoAction = []
                    #save input for training neural net later
                    origSize = []
                    for bot in bots:
                        origSize.append( bot.SaveInput() )
                    for i in range(NUM_BOTS):
                        infoAction.append("")
                        numTypes = len(bots[i].rets.items())
                        numPick = len(bots[i].objectList) + len(RET_NAMES)
                        zones = bots[i].ScoreZoneCheck()
                        #batchOutput = pipes[i][0].recv()
                        batchInput = bots[i].inputs[-SEQ_LEN:]
                        while len(batchInput) < SEQ_LEN:
                            batchInput.append([0] * INPUT_SIZE)
                        batchOutput = nw.probs.eval(feed_dict = {nw.next_element["input"]: [batchInput]}, session = nw.sess)[0]
                        bots[i].RNNInputs.append(batchInput)
                        output = batchOutput
                        latestIdx = np.argmax(output)
                        latestVal = output
                        bots[i].SaveLogits(output.tolist())
                        #idx = np.argmax(output)
                        if np.random.uniform() >= 0:#1-((START+context.count)/NUM_GAMES):
                            idx = latestIdx
                            #idx = np.random.choice(range(0,OUTPUT_SIZE),p = output)
                        else:
                            # default probability distribution, such that 1/3 of the time it moves, 1/3 it picks stuff up, 1/3 it drops off
                            # makes sure bot has variety of experiences
                            prob = [] 
                            for j in range(MVMT_TYPE_SIZE):
                                prob.append(1/(MVMT_TYPE_SIZE * 3))
                            for j in range(numTypes):
                                prob.append(1/(numTypes * 3))
                            for j in range(numPick):
                                prob.append(1/(numPick * 3))
                           # idx = np.random.choice(MVMT_TYPE_SIZE + numTypes + numPick, p = prob)
                            idx = np.random.choice(range(0,OUTPUT_SIZE))
                        action = idx
                        if forwardFlag:
                            idx = 0
                            print(idx)
                        elif backFlag:
                            idx = 1
                            print(idx)
                        elif rightFlag:
                            idx = 2
                            print(idx)
                        elif leftFlag:
                            idx = 3
                            print(idx)
                        elif dropFlag:
                            idx = MVMT_TYPE_SIZE
                            print(idx)
                        elif pickupFlag:
                            if len(zones) > 0:
                                idx = MVMT_TYPE_SIZE + numTypes 
                            else:
                                idx = MVMT_TYPE_SIZE + numTypes
                            print(idx)
                        if idx < MVMT_TYPE_SIZE:
                            mvmt = bots[i].mvmtKey[idx] # get appropriate movement based on nn output
                            infoAction[-1] += (mvmt.__name__)
                            mvmt(bots[i],SCALE * ACTION_TIMING) # execute movement
                            
                        elif idx < MVMT_TYPE_SIZE + numTypes:
                            idx -= MVMT_TYPE_SIZE
                            #logic for dropping off rets 
                            bots[i].DropOffNearest(RET_NAMES[idx])
                            infoAction[-1] += " DROPOFF" + str(RET_NAMES[idx])
                            idx+=MVMT_TYPE_SIZE
                        else:
                            idx-=(MVMT_TYPE_SIZE+numTypes)
                            #logic for picking stuff up
                            bots[i].PickUpNearest(RET_NAMES[idx])
                            idx+=MVMT_TYPE_SIZE+numTypes
                        #action.append(idx)
                        bots[i].SaveAction(action)
                        for name in RET_NAMES:
                            infoAction[-1]+= " " + name + ": " + str(len(bots[i].rets[name])) 
                        
                #stuff done every second
                if not int(context.gameTime - dt) == int(context.gameTime):
                    #update scale and switch scores
                    scaleChange = scaleScore(scales)
                    switchChanges = switchScore(switches)
                    prevRed, prevBlue = vaultScore(vaults, prevRed, prevBlue)
                    if MODE == "DRAW":
                        infoAction[-1]+= " scale: " + str(scaleChange) + " switches: " + str(switchChanges)
                        # update infowindow
                        infoPipe[0].send(infoAction)
                        pass
                    print(str(context.gameTime) + " " + str(context.redScore.val) + " " + str(context.blueScore.val) +" " + str(context.count) + " " + str(latestIdx) + " " + str(latestVal))
                    #save scores
                    for bot in bots:
                        bot.SaveReward()
                if MODE == "DRAW":
                ### Flip screen
                    pygame.display.flip()
                    clock.tick()
                    pygame.display.set_caption("fps: " + str(clock.get_fps()) + " red: " + str(context.redScore.val) + " blue: " + str(context.blueScore.val)+ " " + str(vaults[0].numRet) + " " + str(vaults[1].numRet))
            
            inputs = []
            actions = []
            rewards = []
            logits = []
            print("sending data")
            for bot in bots:
                bot.AssignReward()
                inputs.extend(bot.RNNInputs)
                actions.extend(bot.actions)
                rewards.extend(bot.rewards)
                logits.extend(bot.logits)
            pipe.send([inputs, actions, rewards, logits])
            print("sim done")
            Reset()