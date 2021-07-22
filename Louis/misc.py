import json, pickle, time, copy
from Louis.ARC_data.objects import *

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
            pair['output'] = objects_to_grid(pair['output'], n, m, supple=True)