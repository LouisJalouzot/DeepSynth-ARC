import json, pickle, time, copy
from Louis.ARC_data.objects import *
from program import *

def pickle_read(filename):
    with open(filename, 'rb') as f:
        ret = pickle.load(f)
    return ret

def pickle_write(filename, data):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

def json_read(filename):
    with open(filename, 'r') as f:
        ret = json.load(f)
    return ret

def json_write(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)
        
def speed_test(generator, steps, show=False):
    start = time.time()
    for _ in range(steps):
        p = next(generator)
        if show: print(p)
    print(time.time() - start)
    
def empty_grid_obj_overlap(objects):
    empty = True
    points = set()
    for obj in objects:
        x, y = obj.low
        for i, j, c in obj.points:
            if c != 0 and 0 <= i + x < 30 and 0 <= j + y < 30:
                if (i + x, j + y) in points: raise Exception('Objects overlap')
                points.add((i + x, j + y))
                empty = False
    if empty: raise Exception('Empty grid')
    
def try_pb_p(dsl, p, pb):
    for mode in pb:
        for pair in pb[mode]:
            objects, _, _ = pair['input']
            res = p.eval_naive(dsl, (copy.deepcopy(objects), None))
            if res == objects: raise Exception('Identity program')
            empty_grid_obj_overlap(res)
            pair['output'] = res
    constant = True
    l = [pair['output'] for mode in pb for pair in pb[mode]]
    for objects1 in l:
        for objects2 in l:
            if objects1 != objects2: constant = False
    if constant: raise Exception('Constant program')

def pb_to_grid(pb):
    for mode in pb:
        for pair in pb[mode]:
            objects, n, m = pair['input']
            pair['input'] = objects_to_grid(objects, n, m)
            try: pair['output'] = objects_to_grid(pair['output'], n, m, supple=True)
            except: pair['output'] = [[]]
            
def appear_var(p):
    if isinstance(p, Variable): return True
    if isinstance(p, Lambda): return appear_var(p.body)
    if isinstance(p, Function): return appear_var(p.function) or any(appear_var(arg) for arg in p.arguments)
    return False 
            
def scan_sanity(p):
    if isinstance(p, Function):
        if isinstance(p.function, BasicPrimitive):
            if p.function.primitive == 'if':
                if not appear_var(p.arguments[0]): return False
                if len(p.arguments) > 2 and p.arguments[1] == p.arguments[2]: return False
            if p.function.primitive == 'eq?' and len(p.arguments) > 1 and p.arguments[0] == p.arguments[1]: return False
            if p.function.primitive == 'car' and p.arguments != [] and isinstance(p.arguments[0], Function) and isinstance(p.arguments[0].function, BasicPrimitive) and (p.arguments[0].function.primitive == 'singleton' or p.arguments[0].function.primitive == 'cons'): return 0
        return scan_sanity(p.function) and all(scan_sanity(arg) for arg in p.arguments)
    return True