from type_system import *
from Louis.ARC.objects import *

primitive_types = {
    'FIND_OBJECTS': Arrow(List(List(COLOR)), List(OBJ)),
    'FIND_OBJECTS_POINT': Arrow(List(List(COLOR)), List(OBJ)),
    'FIND_OBJECTS_COLOR': Arrow(List(List(COLOR)), List(OBJ)),
    'FIND_OBJECTS_POINT_COLOR': Arrow(List(List(COLOR)), List(OBJ)),
}

semantics = {
    'FIND_OBJECTS': lambda grid: find_objects(grid, cohesion_type = 'contact'),
    'FIND_OBJECTS_POINT': lambda grid: find_objects(grid, cohesion_type = 'contact by point'),
    'FIND_OBJECTS_COLOR': lambda grid: find_objects(grid, cohesion_type = 'contact and color'),
    'FIND_OBJECTS_POINT_COLOR': lambda grid: find_objects(grid, cohesion_type = 'contact by point and color')
}