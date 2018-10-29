from Global import *

def beginBotPickup(arbiter,space, data):
    context = data[0]
    bot = context.objects[arbiter.shapes[0]._get_shapeid()]
    pickupZone = context.objects[arbiter.shapes[1]._get_shapeid()]
    if bot.color == pickupZone.color:
        bot.canPickup = True
    return True

def endBotPickup(arbiter, space, data):
    context = data[0]
    bot = context.objects[arbiter.shapes[0]._get_shapeid()]
    pickupZone = context.objects[arbiter.shapes[1]._get_shapeid()]
    try:
        if bot.color == pickupZone.color:
            bot.canPickup = False
    except:
        pass
    return True

def beginFieldRet(arbiter,space, data):
    context = data[0]
    context.objects[arbiter.shapes[0]._get_shapeid()].owner.canPickup = True
    return True

def endFieldRet(arbiter, space, data):
    context = data[0]
    try:
        context.objects[arbiter.shapes[0]._get_shapeid()].owner.canPickup = False
    except:
        pass
    return True

def beginBotScore(arbiter, space, data):
    context = data[0]
    bot = context.objects[arbiter.shapes[0]._get_shapeid()]
    zone = context.objects[arbiter.shapes[1]._get_shapeid()]
    if bot.color == zone.color:
        context.objects[arbiter.shapes[0]._get_shapeid()].canScore = True
    return True

def endBotScore(arbiter, space, data):
    context = data[0]
    try:
        bot = context.objects[arbiter.shapes[0]._get_shapeid()]
        zone = context.objects[arbiter.shapes[1]._get_shapeid()]
        if bot.color == zone.color:
            context.objects[arbiter.shapes[0]._get_shapeid()].canScore = False
    except:
        pass
    return True

def beginBotVault(arbiter, space, data):
    context = data[0]
    bot = context.objects[arbiter.shapes[0]._get_shapeid()]
    vault = context.objects[arbiter.shapes[1]._get_shapeid()]
    if bot.color == vault.color:
        bot.canScore = True
    return True

def endBotVault(arbiter, space, data):
    context = data[0]
    try:
        bot = data[0].objects[arbiter.shapes[0]._get_shapeid()]
        vault = data[0].objects[arbiter.shapes[1]._get_shapeid()]
        if bot.color == vault.color:
            bot.canScore = False
    except:
        pass
    return True

def duringBotPlatform(arbiter, space, data):
    context = data[0]
    bot = context.objects[arbiter.shapes[0]._get_shapeid()]
    slope = context.objects[arbiter.shapes[1]._get_shapeid()]
    bot.force += slope.GetForce(bot)
    return True

def beginBotScalePenalty(arbiter, space, data):
    context = data[0]
    bot = context.objects[arbiter.shapes[0]._get_shapeid()]
    bot.score.val -= FOUL_POINTS
    return True

def duringBotBot(arbiter, space, data):
    context = data[0]
    if int(context.gameTime - 1/NUM_STEPS) != int(context.gameTime): #penalize both bots each second
        context.objects[arbiter.shapes[0]._get_shapeid()].score.val -= FOUL_POINTS
        context.objects[arbiter.shapes[1]._get_shapeid()].score.val -= FOUL_POINTS
    return True
