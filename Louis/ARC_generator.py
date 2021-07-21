import sys, copy, matplotlib.pyplot as plt, json, pickle, copy
sys.path.insert(0, '..')
from program import *
from pcfg import *
from dsl import *
from Louis.ARC_data.ARC import *
from Louis.ARC_data.objects import *
from Louis.solutions import *
from Louis.misc import *
from Louis.grids import *
from Algorithms.heap_search import *
from Louis.Algo.bfs_2 import *
from Algorithms.dfs import *

dsl_DS = DSL(DS_semantics, DS_primitive_types)
dsl_paperwork = DSL(paperwork_semantics, paperwork_primitive_types)
dsl = DSL(semantics, primitive_types)
set_types = dsl.instantiate_polymorphic_types(10, True)
forced_types = {OBJ, COLOR}

##### Difficulty 1 #####
def generate_diff_I(max_program_depth = 4):
    pcfgs, cfgs = {}, {}
    for type_ in set_types:
        try:
            type_request = Arrow(OBJ, type_)
            pcfg = dsl_DS.DSL_to_Uniform_PCFG(type_request, max_program_depth=max_program_depth, forced_types=forced_types)
            pcfgs[type_request] = pcfg
        except: print("Impossible green type :", type_)
    for type1 in pcfgs:
        for type2 in pcfgs:
            try:
                type_request = Arrow(type1, Arrow(type2, Arrow(List(OBJ), List(OBJ))))
                print(type_request)
                cfg = dsl_paperwork.DSL_to_Uniform_PCFG(type_request, max_program_depth=max_program_depth, forced_types=forced_types)
                cfgs[type1, type2] = cfg
            except: print("Impossible red type : {} -> {}".format(type1, type2))
    data = pcfgs, cfgs
    pickle_write('ARC_data/diff_I_data.pickle', data)

# generate_diff_I()

def appears(p, i):
    if isinstance(p, Variable): return i == p.variable
    if isinstance(p, Lambda): return appears(p.body, i+1)
    if isinstance(p, Function):
        if appears(p.function, i): return True   
        for arg in p.arguments:
            if appears(arg, i): return True
    return False   

def decrease_vars(p, j = 0):
    if isinstance(p, Variable):
        if p.variable > j: p.variable -= 1
    if isinstance(p, Lambda): decrease_vars(p.body, j+1)
    if isinstance(p, Function):
        decrease_vars(p.function, j)
        for arg in p.arguments: decrease_vars(arg, j)
         
def simplify(p):
    if not appears(p, 2): return 0
    a, b = appears(p, 1), appears(p, 0)
    if a and b:
        return 3
    elif b:
        decrease_vars(p, 1)
        return 1
    elif a:
        decrease_vars(p)
        return 2
    else: return 0

def diff_I_generator(nb_green=25, nb_red=1000):
    pcfgs, cfgs = pickle_read('ARC_data/diff_I_data.pickle')
    reds = {}
    for type1, type2 in cfgs:
        reds[type1, type2], reds[type1], reds[type2] = [], [], []
    for type1, type2 in cfgs:
        k = 0
        for p1 in bfs(cfgs[type1, type2]):
            k += 1
            if k > nb_red: break
            p1 = reconstruct_from_compressed(p1, List(OBJ))
            q1 = copy.deepcopy(p1)
            a = simplify(q1)
            if a == 0: continue
            if a == 1:
                if q1 in reds[type2]: continue
                else: reds[type2].append(q1)
            if a == 2:
                if q1 in reds[type1]: continue
                else: reds[type1].append(q1)
            if a == 3:
                if q1 in reds[type1, type2]: continue
                else: reds[type1, type2].append(q1)
            i = 0
            for p2 in pcfgs[type1].sampling():
                if i > nb_green: break
                i += 1
                if a == 2:
                    yield Function(Lambda(q1), [Lambda(p2)])
                    continue
                j = 0
                for p3 in pcfgs[type2].sampling():
                    i += 1
                    j += 1
                    if a == 1:
                        if j > nb_green: break
                    elif j * j > nb_green: break
                    if a == 3: yield Function(Lambda(Lambda(q1)), [Lambda(p3), Lambda(p2)])
                    if a == 1: yield Function(Lambda(q1), [Lambda(p3)])
                if a == 1: break
        
def diff_I_pb_generator(grid_gen, grids_per_program=5, nb_green=25, nb_grids=30, output='objects', watcher_limit=5):
    for p in diff_I_generator(nb_green=nb_green):
        success, k = 0, 0
        watcher = {'Identity program': 0, 'Empty grid': 0, 'Objects overlap': 0}
        for pb, c_type in grid_gen:
            k += 1
            if k > nb_grids: break
            try:
                try_pb_p(dsl, p, pb)
                if output == 'grids': pb_to_grid(pb)
                yield pb, p, c_type
                success += 1
                if success > grids_per_program: break
            except GeneratorExit: return
            except Exception as s:
                if format(s) in watcher:
                    watcher[format(s)] += 1
                    bad_program = None
                    for mis in watcher:
                        if watcher[mis] > watcher_limit: bad_program = mis
                    if bad_program != None: break

if __name__ == '__main__':
    speed_test(diff_I_pb_generator(grid_generator_cor(), 1), 50)
    # for pb, p, c_type in diff_I_pb_generator(grid_generator_aux(), output='grids'):
    #     display_pb(pb, 'Solution : '+str(p)+'\nCohesion type : '+cohesion_types_corresp[c_type])
    #     # figManager = plt.get_current_fig_manager()
    #     # figManager.window.showMaximized()
    #     plt.show(block=False)
    #     if input() == '0':
    #         break
    #     plt.close('all')

    # l = []
    # i = 0
    # n = 10000
    # for data in diff_I_pb_generator(grid_generator_cor(), grids_per_program=5, nb_green=25):
    #     i += 1
    #     l.append(data)
    #     if i > n: break
    #     if (100 * i) % n == 0: print('{}%'.format(int(100*i/n)))
    # pickle_write('../../espace partage remy louis/Louis/diff_I.pickle', l)






########## Difficulty II
def generate_diff_II():
    m = len(set_types)
    
    ################################################################ cfgs_II
    max_program_depth = 3
    pcfgs_I, _ = pickle_read('ARC_data/diff_I_data.pickle') # obj -> t (depth 4)
    cfgs_II = {} # (obj -> t1) -> (obj -> t2) -> list obj -> t' (depth 3)
    i = 0
    n = len(pcfgs_I)
    n = n * n * m
    print('Processing red CFGs for difficulty II')
    print("{} to go".format(n))
    for type1 in pcfgs_I:
        j = 0
        for type2 in pcfgs_I:
            k = 0
            for type3 in set_types:
                i += 1
                if 100 * i % n == 0:
                    print("{}%".format(i/n*100))
                try:
                    type_request = Arrow(type1, Arrow(type2, Arrow(List(OBJ), type3)))
                    cfg = dsl_paperwork.DSL_to_Uniform_PCFG(type_request, max_program_depth=max_program_depth, forced_types=forced_types)
                    if j == 0:
                        cfgs_II[type1] = {}
                        j = 1
                    if k == 0:
                        cfgs_II[type1][type2] = {}
                        k = 1
                    cfgs_II[type1][type2][type3] = cfg
                except:
                    # print("Impossible red type for difficulty II : {} -> {}".format(type1, type2))
                    pass
    pickle_write('ARC_data/cfgs_II.pickle', cfgs_II)
    
    ################################################################ pcfgs_II
    max_program_depth = 3
    cfgs_II = pickle_read('ARC_data/cfgs_II.pickle') # (obj -> t1) -> (obj -> t2) -> list obj -> t' (depth 3)
    pcfgs_II = {}
    i = 0
    l = set(type_ for _, _, type_ in cfgs_II)
    n = len(l)
    n = n * n * m
    print('Processing green PCFGs for difficulty II')
    print("{} to go".format(n))
    for type_1 in l:
        j = 0
        for type_2 in l:
            k = 0
            for type__ in set_types:
                i += 1
                if 100 * i % n == 0:
                    print("{}%".format(i/n*100))
                try:
                    type_request = Arrow(type_1, Arrow(type_2, type__))
                    pcfg = dsl_DS.DSL_to_Uniform_PCFG(type_request, max_program_depth=max_program_depth, forced_types=forced_types)
                    if j == 0:
                        pcfgs_II[type_1] = {}
                        j = 1
                    if k == 0:
                        pcfgs_II[type_1][type_2] = {}
                        k = 1
                    pcfgs_II[type_1][type_2][type__] = pcfg
                except:
    #                 print("Impossible green type for difficulty II :", type_request)
                    pass
    pickle_write('ARC_data/pcfgs_II.pickle', pcfgs_II)
    
    ################################################################ cfgs_II_root
    max_program_depth = 4
    pcfgs_II = pickle_read('ARC_data/pcfgs_II.pickle') # t'1 -> t'2 -> t" (depth 3)
    # pcfgs_II = pickle_read('ARC_data/pcfgs_II_big.pickle') # t'1 -> t'2 -> t" (depth 4)
    cfgs_II_root = {} # t"1 -> t"2 -> list obj -> list obj (depth 3)
    i = 0  
    l = set(type__ for _, _, type__ in pcfgs_II)
    n = len(l)
    n = n * n * m
    print('Processing root red CFGs for difficulty II')
    print("{} to go".format(n))       
    for type__1 in l:
        j = 0
        for type__2 in l:
            try:
                i += 1
                if 100 * i % n == 0:
                    print("{}%".format(int(i/n*100)))
                type_request = Arrow(type__1, Arrow(type__2, Arrow(List(OBJ), List(OBJ))))
                cfg = dsl_paperwork.DSL_to_Uniform_PCFG(type_request, max_program_depth=max_program_depth, forced_types=forced_types)
                if j == 0:
                    cfgs_II_root[type__1] = {}
                    j = 1
                cfgs_II_root[type__1][type__2] = cfg
            except:
                # print("Impossible root red type for difficulty II :", type_request)
                pass
    pickle_write('ARC_data/cfgs_II_root.pickle', cfgs_II_root)
    
# generate_diff_II()

def diff_II_generator_pcfgs_I(pcfgs_I, t):
    for p in pcfgs_I[t].sampling():
        yield Lambda(p)

def diff_II_generator_cfgs_II(cfgs_II, pcfgs_I, t_):
    for t2 in cfgs_II[t_]:
        for p2 in diff_II_generator_pcfgs_I(pcfgs_I, t2):
            for t1 in cfgs_II[t_][t1]:
                for p1 in diff_II_generator_pcfgs_I(pcfgs_I, t1):
                    for p in bfs(cfgs_II[t_][t1][t2]):
                        yield Function(Lambda(Lambda(p)), [p1, p2, Variable(0)])

def diff_II_generator_pcfgs_II(pcfgs_II, cfgs_II, pcfgs_I, t__):
    for t_2 in pcfgs_II[t__]:
        for p2 in diff_II_generator_cfgs_II(cfgs_II, pcfgs_I, t_2):
            for t_1 in pcfgs_II[t__][t_1]:
                for p1 in diff_II_generator_cfgs_II(cfgs_II, pcfgs_I, t_1):
                    for p in pcfgs_II[t__][t_1][t_2].sampling():
                        yield Function(Lambda(Lambda(p)), [p1, p2])

def diff_II_generator():
    cfgs_II_root = pickle_read('ARC_data/cfgs_II_root.pickle') # cfgs_II_root[t"2][t"1] = CFG(t"1 -> t"2 -> list obj -> list obj) (depth 3)
    pcfgs_II = pickle_read('ARC_data/pcfgs_II.pickle') # t'1 -> t'2 -> t" (depth 3)
    cfgs_II = pickle_read('ARC_data/cfgs_II.pickle') # (obj -> t1) -> (obj -> t2) -> list obj -> t' (depth 3)
    pcfgs_I, _ = pickle_read('ARC_data/diff_I_data.pickle') # obj -> t (depth 4)
    for t__2 in cfgs_II_root:
        for p2 in diff_II_generator_pcfgs_II(pcfgs_II, cfgs_II, pcfgs_I, t__2):
            for t__1 in cfgs_II_root[t__2]:
                for p1 in diff_II_generator_pcfgs_II(pcfgs_II, cfgs_II, pcfgs_I, t__1):
                    for root in bfs(cfgs_II_root[t__2][t__1]):
                        yield Function(Lambda(Lambda(reconstruct_from_compressed(root, List(OBJ)))), [p1, p2])
    
    
            
################################################################ OLD
# def diff_I():
#     with open('ARC_data/diff_I_data.pickle', 'rb') as f:
#         pcfgs, cfgs = pickle.load(f)

#     with open('ARC/data/training/a61ba2ce.json') as json_file: #1cf80156 3de23699
#         pb = json.load(json_file)
#         objects = find_objects(pb['train'][0]['input'])
#         # display(objects_to_grid(objects))
#         # pb_ans = {}
#         # pb_ans['train'] = [p_1cf80156.eval(dsl, (find_objects(pb['train'][i]['input']), None), p_1cf80156.hash+i) for i in range(3)]
#         # pb_ans['test'] = p_1cf80156.eval(dsl, (find_objects(pb['test'][0]['input']), None), p_1cf80156.hash+3)
#         # display(objects_to_grid(p_1cf80156.eval(dsl, (find_objects(pb['train'][0]['input']), None), p_1cf80156.hash)))
#         # display(objects_to_grid(p_1cf80156.eval(dsl, (find_objects(pb['train'][1]['input']), None), p_1cf80156.hash+1)))
#         # display(objects_to_grid(p_1cf80156.eval(dsl, (find_objects(pb['train'][2]['input']), None), p_1cf80156.hash+2)))
#         # display(objects_to_grid(p_1cf80156.eval(dsl, (find_objects(pb['test'][0]['input']), None), p_1cf80156.hash+3)))
#         # plt.show()

#     good, bad = 0, 0
#     for type1, type2 in cfgs:
#         k = 0
#         # print("TYPE1 : {}\nTYPE2 : {}\n".format(type1, type2))
#         for p1 in bfs(cfgs[type1, type2]):
#             k += 1
#             if k > 5:
#                 break
#             # print(p1)
#             # p1 : (obj -> t1) -> (obj -> t2) -> list obj -> list obj
#             p1 = Lambda(reconstruct_from_compressed(p1, List(OBJ)))
#             for _ in range(1):
#                 # p2 : obj -> t1
#                 p2 = heap_search(pcfgs[type1]).__next__()
#                 # p3 : obj -> t2
#                 p3 = heap_search(pcfgs[type2]).__next__()
#                 assembled_program = Function(Lambda(Lambda(p1)), [Lambda(p3), Lambda(p2)])                       
#                 try:
#                     # for i in range(3):
#                     #     grid = pb['train'][i]['input']
#                     #     res = assembled_program.eval(dsl, (find_objects(grid), None), assembled_program.hash+i)
#                     #     if res != pb_ans['train'][i]:
#                     #         raise Error
#                     # print(assembled_program)
#                     res = assembled_program.eval_naive(dsl, (copy.deepcopy(objects), None))
#                     # print(assembled_program)
#                     # print(res)
#                     res = objects_to_grid(res)
#                     good += 1
#                     if good % 700 == 0:
#                         print("Good :", assembled_program)
#                         # display(res)
#                 except:
#                     if bad % 500 == 0:
#                         print("Bad :", assembled_program)
#                     bad += 1

#     print("good : {}\nbad : {}\nPercentage : {}%".format(good, bad, int(100 * good / (good + bad))))
#     plt.show()
    
# def diff_I_pb_generator(grid_gen, grids_per_program=5, nb_green=25, nb_grids=100, output='objects'):
#     good, bad = 0, 0
#     for p in diff_I_generator(nb_green=nb_green):
#         k, success = 0, 0
#         for pb, c_type in grid_gen:
#             k += 1
#             if k > nb_grids:
#                 bad += 1
#                 # print('program fail', p, cohesion_types_corresp[c_type], '\n')
#                 break
#             try:
#                 for mode in pb:
#                     for pair in pb[mode]:
#                         objects, n, m = pair['input']
#                         res = p.eval_naive(dsl, (copy.deepcopy(objects), None))
#                         if res == objects: raise ValueError
#                         safe = False
#                         for obj in res:
#                             x, y = obj.low
#                             for i, j, c in obj.points:
#                                 if c != 0 and 0 <= i + x < 30 and 0 <= j + y < 30:
#                                     safe = True
#                                     break
#                             if safe:
#                                 break
#                         if not safe: raise ValueError
#                         pair['output'] = res, n, m
#                 # display_pb(pb)
#                 # print(p)
#                 # plt.show(block=False)
#                 # a = input()
#                 # if a == '0':
#                 #     return
#                 # plt.close()
#                 safe = False
#                 for pair1 in pb['train']:
#                     if pair1['output'][0] != pb['test'][0]['output'][0]:
#                         safe = True
#                         break
#                     for pair2 in pb['train']:
#                         if pair1['output'][0] != pair2['output'][0]:
#                             safe = True
#                             break
#                     if safe:
#                         break
#                 if not safe: raise ValueError # constant program
#                 if output == 'grids':
#                     for mode in pb:
#                         for pair in pb[mode]:
#                             for io in pair:
#                                 objects, n, m = pair[io]
#                                 pair[io] = objects_to_grid(objects, n, m, supple=(io=='output'))
#                 good += 1
#                 yield pb, p, c_type
#                 success += 1
#                 if success > grids_per_program:
#                     break
#             except:
#                 pass
#         # print(good, bad)