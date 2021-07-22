from type_system import *
from Louis.ARC_data.objects import *
from functools import reduce

OBJ = PrimitiveType('obj')
COLOR = PrimitiveType('color')
t0 = PolymorphicType('t0')
t1 = PolymorphicType('t1')

def _range(n):
  if n < 100: return list(range(n))
  raise ValueError()

paperwork_primitive_types = {
  # "empty": List(t0),
  "cons": Arrow(t0, Arrow(List(t0), List(t0))),
  "car": Arrow(List(t0), t0),
  # "cdr": Arrow(List(t0), List(t0)),
  "empty?": Arrow(List(t0), BOOL),
  "gt?": Arrow(INT, Arrow(INT, BOOL)),
  "if": Arrow(BOOL, Arrow(t0, Arrow(t0, t0))),
  "eq?": Arrow(t0, Arrow(t0, BOOL)),
  'not': Arrow(BOOL, BOOL),
  'or': Arrow(BOOL, Arrow(BOOL, BOOL)),
  # "*": Arrow(INT, Arrow(INT, INT)),
  "+": Arrow(INT, Arrow(INT, INT)),
  "-": Arrow(INT, INT), # unaire
  #"mod": Arrow(INT, Arrow(INT, INT)),
  "0": INT,
  "1": INT,
  "length": Arrow(List(t0), INT),
  "range": Arrow(INT, List(INT)),
  # 'empty_obj': OBJ
  "map": Arrow(Arrow(t0, t1), Arrow(List(t0), List(t1))),
  # "fold": Arrow(List(t0), Arrow(t1, Arrow(Arrow(t0, Arrow(t1, t1)), t1))),
  'max': Arrow(Arrow(t0, INT), Arrow(List(t0), t0)),
  'filter': Arrow(Arrow(t0, BOOL), Arrow(List(t0), List(t0))),
  'singleton': Arrow(t0, List(t0)),
}

DS_primitive_types = {
  "BLACK": COLOR, "BLUE": COLOR, "RED": COLOR, "GREEN": COLOR, "YELLOW": COLOR, "GRAY": COLOR, "PINK": COLOR, "ORANGE": COLOR, "CYAN": COLOR, "BROWN": COLOR,
  'SAME': Arrow(OBJ, Arrow(OBJ, BOOL)),
  'SAME_COLOR': Arrow(OBJ, Arrow(OBJ, BOOL)),
  'SAME_SHAPE': Arrow(OBJ, Arrow(OBJ, BOOL)),
  'IS_RECTANGLE': Arrow(OBJ, BOOL),
  'DUPLICATE': Arrow(OBJ, OBJ),
  'TRANSLATE': Arrow(INT, Arrow(INT, Arrow(OBJ, OBJ))),
  'RELATIVE_TRANSLATE': Arrow(INT, Arrow(INT, Arrow(OBJ, OBJ))),
  'SYMETRY_X': Arrow(OBJ, OBJ),
  'SYMETRY_Y': Arrow(OBJ, OBJ),
  'ROTATION90': Arrow(OBJ, OBJ),
  'FILL': Arrow(INT, Arrow(INT, Arrow(INT, Arrow(INT, Arrow(COLOR, OBJ))))),
  'CHANGE_COLOR': Arrow(COLOR, Arrow(OBJ, OBJ)),
  '0': INT,
  '1': INT,
  '+': Arrow(INT, Arrow(INT, INT)),
  '-': Arrow(INT, INT), # unaire
  'X_LOW': Arrow(OBJ, INT),
  'Y_LOW': Arrow(OBJ, INT),
  'X_HIGH': Arrow(OBJ, INT),
  'Y_HIGH': Arrow(OBJ, INT),
  'IS_IN': Arrow(INT, Arrow(INT, Arrow(OBJ, BOOL))),
  'COLOR': Arrow(OBJ, COLOR),
  'SIZE': Arrow(OBJ, INT),
}

paperwork_semantics = {
  # "empty" : [],
  "cons" : lambda x: lambda l: [x] + l,
  "car" : lambda l: l[0],
  # "cdr" : lambda l: l[1:],
  "empty?" : lambda l: l == [],
  "gt?" : lambda x: lambda y: x > y,
  "if" : lambda c: lambda t: lambda f: t if c else f,
  "eq?" : lambda x: lambda y: x == y,
  "not": lambda b: not b,
  'or': lambda b1: lambda b2: b1 or b2,
  # "*" : lambda x: lambda y: x * y,
  "+" : lambda x: lambda y: x + y,
  "-" : lambda x: -x, # unaire
  #"mod" : lambda x: lambda y: x % y,
  "0" : 0, "1" : 1,
  "length" : len,
  "range" : _range,
  # 'empty_obj': lambda: Object()
  "map" : lambda f: lambda l: list(map(f, l)),
  # "fold" : lambda l: lambda x0: lambda f: reduce(lambda a, x: f(x)(a), l[::-1], x0),
  'max': lambda key: lambda l: max(l, key=key),
  'filter': lambda p: lambda l: list(filter(p, l)),
  'singleton': lambda x: [x],
}

DS_semantics = {
  "BLACK": 0, "BLUE": 1, "RED": 2, "GREEN": 3, "YELLOW": 4, "GRAY": 5, "PINK": 6, "ORANGE": 7, "CYAN": 8, "BROWN": 9,
  'SAME': lambda obj1: lambda obj2: obj1.same(obj2, 'both'),
  'SAME_SHAPE': lambda obj1: lambda obj2: obj1.same(obj2, 'shape'),
  'SAME_COLOR': lambda obj1: lambda obj2: obj1.same(obj2, 'color'),
  'DUPLICATE': lambda obj: obj.duplicate(),
  'TRANSLATE': lambda i: lambda j: lambda obj: obj.translate(i, j, 'absolute'),
  'RELATIVE_TRANSLATE': lambda i: lambda j: lambda obj: obj.translate(i, j, 'relative'),
  'SYMETRY_X': lambda obj: obj.symetry_x(),
  'SYMETRY_Y': lambda obj: obj.symetry_y(),
  'ROTATION90': lambda obj: obj.rotate(),
  'FILL': lambda i: lambda j: lambda x: lambda y: lambda c: fill(i, j, x, y, c),
  'CHANGE_COLOR': lambda c: lambda obj: obj.change_color(c),
  'IS_RECTANGLE': lambda obj: obj.is_rectangle(),
  '0': 0,
  '1': 1,
  '+': lambda i: lambda j: i+j,
  '-': lambda i: -i,
  'X_LOW': lambda obj: obj.low[0],
  'Y_LOW': lambda obj: obj.low[1],
  'X_HIGH': lambda obj: obj.high[0],
  'Y_HIGH': lambda obj: obj.high[1],
  'IS_IN': lambda i: lambda j: lambda obj: len([0 for x, y, _ in obj.points if i == x + obj.low[0] and j == y + obj.low[1]]) > 0,
  'COLOR': lambda obj: obj.color,
  'SIZE': lambda obj: obj.nb_points(),
}

no_repetitions = {
  'SYMETRY_X',
  'SYMETRY_Y',
  'CHANGE_COLOR',
  'DUPLICATE',
  'TRANSLATE',
  'RELATIVE_TRANSLATE',
}

semantics = dict(paperwork_semantics, **DS_semantics)
primitive_types = dict(paperwork_primitive_types, **DS_primitive_types)