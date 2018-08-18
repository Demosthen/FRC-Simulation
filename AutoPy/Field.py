import pymunk
from Global import *
class Field(object):
    """The walls of the field"""
    def __init__(self,context, static_body):
        self.name = FIELD_NAME
        self.context = context
        self.field = [pymunk.Segment(static_body, (SCALE*1.0,SCALE*1.0), (SCALE*(FIELD_LENGTH+1),SCALE*1.0), 0.0),# add 1 to dims to offset field
                    pymunk.Segment(static_body, (SCALE*1.0,SCALE*1.0), (SCALE*1.0,SCALE*(FIELD_WIDTH+1)),0.0),
                    pymunk.Segment(static_body, (SCALE*(FIELD_LENGTH+1),SCALE*1.0), (SCALE*(FIELD_LENGTH+1),SCALE*(FIELD_WIDTH+1)), 0.0),
                    pymunk.Segment(static_body,(SCALE*1.0,SCALE*(FIELD_WIDTH+1)),(SCALE*(FIELD_LENGTH+1),SCALE*(FIELD_WIDTH+1)),0.0),
                    pymunk.Segment(static_body, (SCALE*1.0,SCALE*2.401), (SCALE*(3.714),SCALE*1.0), 0.0),
                    pymunk.Segment(static_body, (SCALE*(FIELD_LENGTH+1),SCALE*2.401), (SCALE*(FIELD_LENGTH - 2.714),SCALE*1.0), 0.0),
                    pymunk.Segment(static_body, (SCALE*1.0,SCALE*(FIELD_WIDTH - 0.401)), (SCALE*(3.714),SCALE*FIELD_WIDTH+1), 0.0),
                    pymunk.Segment(static_body, (SCALE*(FIELD_LENGTH+1),SCALE*(FIELD_WIDTH - 0.401)), (SCALE*(FIELD_LENGTH - 1.714),SCALE*(FIELD_WIDTH+1)), 0.0)]
        for line in self.field:
            line.elasticity = 0
            line.friction = 0.9
            line.filter = pymunk.ShapeFilter(categories = 1, mask = pymunk.ShapeFilter.ALL_MASKS ^ 2)
            line.collision_type = collision_types[FIELD_NAME]
            self.context.objects[line._get_shapeid()] = self
        self.inSpace = False
    def AddToSpace(self):
        if not self.inSpace:
            self.context.space.add(self.field)
            self.inSpace = True


