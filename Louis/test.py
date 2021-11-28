import sys, copy, matplotlib.pyplot as plt, json, pickle
sys.path.insert(0, '..')
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

from Louis.ARC_data.objects import *
from Louis.ARC_data.main import *
from Louis.solutions import *
from Louis.ARC_data.ARC import *
from Louis.misc import *
from Louis.grids import *

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
    with open('ARC_data/pcfg_ARC_%s.pickle' % i, 'wb') as f:
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
            p = Function(Lambda(Lambda(Function(BasicPrimitive('map'), [Variable(0), Variable(2)]))),
                         [BasicPrimitive('0'), Lambda(Function(BasicPrimitive('SYMETRY_X'), [Variable(0)]))])
            print(t, p)
            objects = p.eval_naive(dsl, (var0, None))
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
            
    plt.show()
    
# ARC()

# p1 = Function(BasicPrimitive('ROTATION90'), [Variable(0)])
# p2 = Function(BasicPrimitive('map'), [Variable(0), Variable(1)])
# p = Function(Lambda(p2), [Lambda(p1)])

# i = 0
# with open('ARC/data/training/1f85a75f.json') as json_file:
#         pb = json.load(json_file)
#         grid = pb['train'][i]['input']
#         display(grid)
#         var0 = find_objects(grid, 'color')
#         var0[0].display()
        # print(var0)
        # print(p_a87f7484)
        # objects = p_a87f7484.eval(dsl, (var0, None), p_a87f7484.__hash__)
        # objects = p.eval_naive(dsl, (var0, None))
        # print(p)
        # print(objects)
        # display(objects_to_grid(objects))
        # display(pb['train'][i]['output'])
        # display(objects_to_grid(Function(BasicPrimitive('map'), [BasicPrimitive('ROTATION90'), Variable(0)]).eval(dsl, (var0, None), 276427)))
        
# plt.show()

# i = 0
# l = []
# for name in solutions:
#     i += 1
#     if i < 0: continue
#     pb = json_read('ARC/data/training/'+name)
#     p = solutions[name]
#     display_pb(pb)
#     for mode in pb:
#         for pair in pb[mode]:
#             objects = find_objects(pair['input'], cohesions[name], background_color[name])
#             pair['input'] = objects, len(pair['input']), len(pair['input'][0])
#     try_pb_p(dsl, p, pb)
#     pb_to_grid(pb)
#     display_pb(pb, format(p))
#     plt.show(block=False)
#     input()
#     plt.close('all')
    
#     if background_color[name] == 0: l.append((pb, p, cohesions[name]))

# pickle_write('../../espace partage remy louis/solutions.pickle', l)

name = '3de23699'
pb = json_read('ARC/data/training/'+name+'.json')
k = 0
for x, _ in grid_generator(1000):
    for mode in pb:
        for pair in pb[mode]:
            for io in pair:
            # for obj in pair['input'][0]:
            #     if obj.nb_points() < 5: continue
            #     obj.points = [(0, 0, 3), (1, 0, 3), (0, 1, 3), (1, 2, 6), (2, 1, 6)]
                img = pair[io]
                display(img)
                plt.show(block=False)
                if input() == '0':
                    plt.close('all')
                    plt.gca().set_axis_off()
                    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
                    plt.margins(0,0)
                    plt.gca().xaxis.set_major_locator(plt.NullLocator())
                    plt.gca().yaxis.set_major_locator(plt.NullLocator())
                    n, m = len(img), len(img[0])
                    img_ = np.zeros((max(n, m), max(n, m)))
                    for i in range(n):
                        for j in range(m): img_[n - i - 1][j] = img[i][j]
                    plt.pcolormesh(img_, cmap=cmap, norm=norm, edgecolor='xkcd:dark gray', linewidth=.01)
                    # plt.show()
                    plt.savefig(f"{k}.png", bbox_inches='tight', pad_inches=0.0)
                    k += 1
                plt.close('all')
    break