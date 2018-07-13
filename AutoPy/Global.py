
from Int import Int
from collections import defaultdict
NUM_BOTS = 6
NUM_ZONES = 2
NUM_RET = 20
FIELD_WIDTH = 27
FIELD_LENGTH = 54

BOT_NAME = "Bot"
PICKUP_NAME = "Pickup"
SCALE_NAME = "Scale"
VAULT_NAME = "Vault"
SWITCH_NAME = "Switch"
PENALTY_NAME = "Penalty"
OBSTACLE_NAME = "Obstacle"
CUBE_NAME = "Cube"
VISFIELD_NAME = "VisField"
STEP_SIZE = 60.0

SCALE_POINTS = 1
SWITCH_POINTS = 1
VAULT_POINTS = 5
collision_types = {BOT_NAME:1,
                   PICKUP_NAME:2,
                   SCALE_NAME:3,
                   VAULT_NAME:4,
                   SWITCH_NAME:5,
                   PENALTY_NAME:6,
                   OBSTACLE_NAME:7,
                   CUBE_NAME:8,
                   VISFIELD_NAME:9}
RET_NAMES = [CUBE_NAME] # list of all rets in game
SCORE_NAMES = [SCALE_NAME, SWITCH_NAME, VAULT_NAME]
SCALE_RETKEY = {CUBE_NAME: True}
SWITCH_RETKEY = {CUBE_NAME: True}
VAULT_RETKEY = {CUBE_NAME: True}
redScore = Int(0)
blueScore = Int(0)
objects = defaultdict(lambda:None)
scale = 20
grav3d = 32.2# accel due 2 grav in ft