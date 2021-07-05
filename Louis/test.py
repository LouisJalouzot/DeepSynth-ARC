from type_system import *
from cons_list import *
from program import *
from cfg import *
from pcfg import *
from dsl import *

# Import algorithms
from Algorithms.heap_search import heap_search
from Algorithms.a_star import a_star
from Algorithms.threshold_search import threshold_search
from Algorithms.dfs import dfs
from Algorithms.bfs import bfs
from Algorithms.sqrt_sampling import sqrt_sampling

from ARC.objects import *
from sols import *
import pickle, json
import matplotlib.pyplot as plt
from ARC.ARC import semantics, primitive_types

dsl = DSL(semantics = semantics, primitive_types = primitive_types)
#print(dsl)

t = Arrow(List(OBJ), List(OBJ))
# t = Arrow(OBJ, OBJ)

def ARC():
    i = 4
    # with open('ARC_testing/pcfg_ARC_%s.pickle' % i, 'rb') as f:
    #     pcfg = pickle.load(f)
    # print(len(pcfg.rules))

    pcfg = dsl.DSL_to_Random_PCFG(t, max_program_depth=i)
    with open('ARC_testing/pcfg_ARC_%s.pickle' % i, 'wb') as f:
        pickle.dump(pcfg, f)

    d = False
    b = False
    with open('ARC/data/training/a3325580.json') as json_file: #1cf80156 3de23699
        pb = json.load(json_file)
        grid = pb['train'][0]['input']
        display(grid)
        if d: plt.show(block=b)
        var0 = find_objects(grid)
        # print([obj.display('object') for obj in var0])
        i = 0
        # p = Function(BasicPrimitive("SYMETRY_X"), [Variable(0)])
        # print(p)
        # print(p.eval(dsl, (var0, None), p.__hash__).display('object'))
        for p in pcfg.sampling():
            #try:
            # p = Function(BasicPrimitive('XCOORD_LOW'),[Function(BasicPrimitive('ACCESS'),[BasicPrimitive('0'),Variable(0)])])
            print(t, p)
            objects = p.eval(dsl, (var0, None), p.__hash__)
                # if any([True for obj in objects if obj == None]):
                #     raise TypeError
            #    try:
            display(objects_to_grid(objects))
            if d: plt.show(block=b)
            #     except:
            #         print("Failure display")
            # except:
            #     print("Failure eval")
            # for obj in objects:
            #     print(objects)
            i += 1
            if i > 0:
                break
            print("\n")
            
    # plt.show()
    
# ARC()

p1 = Function(BasicPrimitive('ROTATION90'), [Variable(0)])
p2 = Function(BasicPrimitive('map'), [Variable(0), Variable(1)])
p = Function(Lambda(p2), [Lambda(p1)])

i = 2
with open('ARC/data/training/a87f7484.json') as json_file:
        pb = json.load(json_file)
        grid = pb['train'][i]['input']
        display(grid)
        var0 = find_objects(grid, 'contact by point and color')
        # print(var0)
        # print(p_a87f7484)
        # objects = p_a87f7484.eval(dsl, (var0, None), p_a87f7484.__hash__)
        objects = p.eval_naive(dsl, (var0, None))
        print(p)
        # print(objects)
        display(objects_to_grid(objects))
        # display(pb['train'][i]['output'])
        # display(objects_to_grid(Function(BasicPrimitive('map'), [BasicPrimitive('ROTATION90'), Variable(0)]).eval(dsl, (var0, None), 276427)))
        
plt.show()