
from Int import Int
from collections import defaultdict
from pymunk import Vec2d
#CONSTANTS
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
SCALE_PENALTY_NAME = "ScalePenalty"
OBSTACLE_NAME = "Obstacle"
CUBE_NAME = "Cube"
VISFIELD_NAME = "VisField"
RETFIELD_NAME = "RetField"
PLATFORM_NAME = "Platform"
FIELD_NAME = "Field"

NUM_STEPS = 60.0 # per sec for physics
GAME_DURATION = 110 #2 mins 15 secs (teleop duration) minus 25 secs for climb 
SCALE_POINTS = 1 # per sec
SWITCH_POINTS = 1
VAULT_POINTS = 5# one time
FOUL_POINTS = 1
TECH_FOUL_POINTS = 25
collision_types = {BOT_NAME:1,
                   PICKUP_NAME:2,
                   SCALE_NAME:3,
                   VAULT_NAME:4,
                   SWITCH_NAME:5,
                   SCALE_PENALTY_NAME:6,
                   OBSTACLE_NAME:7,
                   CUBE_NAME:8,
                   VISFIELD_NAME:9,
                   RETFIELD_NAME:10,
                   PLATFORM_NAME:11,
                   FIELD_NAME:12}
inv_collision_types = {v: k for k,v in collision_types.items()} # inverse dict for reverse lookup
RET_NAMES = [CUBE_NAME] # list of all rets in game
SCORE_NAMES = [SCALE_NAME, SWITCH_NAME, VAULT_NAME]
TO_RESET = [CUBE_NAME, SWITCH_NAME, BOT_NAME, SCALE_NAME]
# dicts of what retrievables each scorezone can take
SCALE_RETKEY = {CUBE_NAME: True}
SWITCH_RETKEY = {CUBE_NAME: True}
VAULT_RETKEY = {CUBE_NAME: True}
PICKUP_RETKEY = {CUBE_NAME: True}
PENALTY_RETKEY = {CUBE_NAME: False}
SCALE = 20 # makes stuff look bigger on screen
GRAV3D = 32.2# accel due to grav in ft
INPUT_SIZE = 50

NN_PROC_NAME = "nn"
SIM_PROC_NAME = "sim"

SEQ_LEN = 15
BATCH_SIZE = 32
MVMT_TYPE_SIZE = 5
OUTPUT_SIZE = MVMT_TYPE_SIZE + len(RET_NAMES) + len(RET_NAMES)
CORRECTION = 0.000001 # to make sure gradients are nonzero
ACTION_TIMING = 6 #how many physics steps before each action
BOT_START_POS = [Vec2d((3,5)),
                 Vec2d((3,(FIELD_WIDTH+1)/2)),
                 Vec2d(3,FIELD_WIDTH-3),
                 Vec2d(FIELD_LENGTH-1,5),
                 Vec2d(FIELD_LENGTH-1,(FIELD_WIDTH+1)/2),
                 Vec2d(FIELD_LENGTH-1,FIELD_WIDTH-3)]

MODE = "SIM"#SIM or DRAW
RESTORE_MODEL = False # 90 0.9
EPSILON = 0.9 # 0 = max exploitation, 1 = max exploration
START = 0
NUM_SIMS = 4
NUM_GAMES = 1000
# add RET_DIMS variable later