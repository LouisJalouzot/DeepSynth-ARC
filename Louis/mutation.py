import sys, copy, matplotlib.pyplot as plt, json, pickle, copy
sys.path.insert(0, '..')

from program import *
from pcfg import *
from dsl import *

from Louis.ARC.ARC import *
from Louis.ARC.objects import *
from Louis.solutions import *
from Louis.grids import *

dsl = DSL(semantics, primitive_types)
same_type = {p: set() for p in primitive_types}
for p in primitive_types:
    for q in primitive_types:
        if primitive_types[p] == primitive_types[q]:
            same_type[p].add(BasicPrimitive(q))

# def mutate_rec(l, f, l_args, i, n):
#     if i == 0:
#         # print("i == 0 : ", [[a] for a in l_args[i]])
#         return [[a] for a in l_args[i]]
#     elif i == n:
#         for args in mutate_rec(l, f, l_args, i-1, n):
#             # print("ARGS : ", args)
#             l.append(Function(f, args))
#     else:
#         aux = []
#         # print(l_args[i])
#         # print(mutate_rec(l, f, l_args, i-1, n))
#         for mutants_arg in mutate_rec(l, f, l_args, i-1, n):
#             for a in l_args[i]:
#                 aux.append(mutants_arg+[a])
#         # print("AUX : ", aux)
#         return aux

# def mutate(s, same_type):
#     if isinstance(s, BasicPrimitive):
#         return list(same_type[s.primitive])
#     elif isinstance(s, Variable):
#         return [Variable(i) for i in range(s.variable + 1)]
#     elif isinstance(s, Lambda):
#         return [Lambda(p) for p in mutate(s.body, same_type)]
#     elif isinstance(s, Function):
#         # print("S : ", s)
#         l = []
#         n = len(s.arguments)
#         # print("S :", s)
#         mutate_args = [mutate(arg, same_type) for arg in s.arguments]
#         # print("mutate_args : ", mutate_args)
#         for f in mutate(s.function, same_type):
#             mutate_rec(l, f, mutate_args, n, n)
#         return l
#     return []

# def mutation(semantics, primitive_types, pb, sol):
#     dsl = DSL(semantics, primitive_types)
#     same_type = {p: set() for p in primitive_types}
#     for p in primitive_types:
#         for q in primitive_types:
#             if primitive_types[p] == primitive_types[q]:
#                 same_type[p].add(BasicPrimitive(q))

#     mutants = mutate(sol, same_type)
#     generated = []
#     for mutant in mutants:
#         try:
#             new_pb = {}
#             for mode in pb:
#                 new_pb[mode] = []
#                 for pair in pb[mode]:
#                     ans = mutant.eval(dsl, (find_objects(pair['input']), None), p.__hash__)
#                     new_pb[mode].append({'input': pair['input'], 'output': objects_to_grid(ans)})
#             generated.append((new_pb, mutant))
#         except:
#             # print("Error eval")
#             ()

#     return generated

def mutate_list(l, i, n, env):
    if i == n:
        raise StopIteration
    else:
        for p in mutate(l[i], env):
            if i >= n - 1:
                l[i] = p
                yield None
            else:
                for _ in mutate_list(l, i+1, n, env):
                    l[i] = p
                    yield None

def mutate(p, env, type_parent=None, ind_arg=None):
    if isinstance(p, BasicPrimitive):
        for q in same_type[p.primitive]:
            yield q
    elif isinstance(p, Variable):
        for i in range(p.variable + 1):
            yield Variable(i)
    elif isinstance(p, Lambda):
        for q in mutate(p.body, env):
            yield Lambda(q)
    elif isinstance(p, Function):
        for f in mutate(p.function, env):
            for _ in mutate_list(p.arguments, 0, len(p.arguments), env):
                yield Function(f, p.arguments)


def build_mutation_pb(max_search=1000000, nb_mutants=1000, nb_grids=5, nb_tries_grids=100, grids_tries=100, output='grids'):
    grid_gen = grid_generator(tries=grids_tries)
    for name in solutions:
        print(name)
        i = 0
        pb = json_read('ARC/data/training/'+name)
        objects = {'train': [], 'test': []}
        for mode in pb:
            objects[mode] = [(find_objects(pair['input'], cohesions[name], background_color[name]), len(pair['input']), len(pair['input'][0])) for pair in pb[mode]]
        
        sol = solutions[name]
        nb = 0
        for _ in mutate(sol, (List(OBJ), None)):
            nb += 1
            if nb > max_search: break
        
        i = -1
        for p in mutate(sol, (List(OBJ), None)):
            i += 1
            if i > nb: break
            if i % max(int(nb / nb_mutants), 1) != 0: continue
            
            ### Grids of the original progam
            try:
                new_pb = {'train': [], 'test': []}
                for mode in objects:
                    for obj_list, n, m in objects[mode]:
                        res = p.eval_naive(dsl, (copy.deepcopy(obj_list), None))
                        if res == obj_list: raise ValueError
                        if output == 'objects':
                            new_pb[mode].append({'input': (obj_list, n, m), 'output': (res, n, m)})
                        else:
                            new_pb[mode].append({'input': objects_to_grid(obj_list, n, m, supple=True), 'output': objects_to_grid(res, n, m, supple=True)})
                yield new_pb, copy.deepcopy(p), cohesions[name]
            except: pass
            
            ### Random grids
            tries, grids = 0, 0
            for pb_random, c_type in grid_gen:
                if tries > nb_tries_grids or grids > nb_grids: break
                tries += 1
                
                try:
                    for mode in pb_random:
                        for pair in pb_random[mode]:
                            objects, n, m = pair['input']
                            if output == 'grids':
                                pair['input'] = objects_to_grid(objects, n, m)
                            res = p.eval_naive(dsl, (copy.deepcopy(objects), None))
                            if res == objects: raise ValueError
                            if output == 'objects':
                                pair['output'] = res, n, m
                            else:
                                pair['output'] = objects_to_grid(res, n, m, supple=True)
                    yield pb_random, copy.deepcopy(p), c_type
                    grids += 1
                except: pass
                
            
# speed_test(build_mutation_pb(), 10000)

i = 0
l = []
for data in build_mutation_pb(nb_mutants=10, nb_grids=1):
    i += 1
    l.append(data)
    # pb, p, c_type = data
    # print(p)
    # display_pb(pb)
    # plt.show()
print(i)
pickle_write('data_for_nn/problems/mutation_10mutants_1grid.pickle', l)

# for pb, p, _ in build_mutation_pb():
#     print(p)+cohesion_types_corresp[c_type]+cohesion_types_corresp[c_type]
#     display_pb(pb)
#     plt.show(block=False)
#     if input() == '0':
#         break
#     plt.close('all')

def get_types(p, t, sub_programs, env):
    if isinstance(p, Variable(0)):
        p.type = index(env, p.variable)
    if isinstance(p, ):
        return

def mutate_II(p, same_type, sub_programs, env, alpha, theta):
    get_types(p, Arrow(List(OBJ), List(OBJ)), sub_programs, env)
    return

def add_set(sub_programs, key, obj):
    if key not in sub_programs:
        sub_programs[key] = set(obj)
    else:
        sub_programs[key].add(obj)

def generate_II(p, alpha=0.5, theta = 0.3):
    same_type = {}
    for p in primitive_types:
        for q in primitive_types:
            if primitive_types[p] == primitive_types[q]:
                add_set(same_type, p, BasicPrimitive(q))
    sub_programs = {}
    for p in primitive_types:
        add_set(sub_programs, primitive_types[p], p)

    env = (List(OBJ), None)
    p.type = Arrow(List(OBJ), List(OBJ))
    for q in mutate_II(p, same_type, sub_programs, env, alpha, theta):
        yield q
        
        
        
def mutate_II_brutal(p, same_type, sub_programs, alpha, theta):
    sub_programs.add(p)
    if np.random.rand() < theta:
        yield np.random.choice(sub_programs)
        
    if isinstance(p, Variable):
        if np.random.rand() < alpha:
            p.variable = np.random.randint(p.variable + 1)
    if isinstance(p, Lambda):
        pass
        
def generate_II_brutal(p, same_type, sub_programs, alpha=0.5, theta=0.2):
    same_type = {}
    for p in primitive_types:
        for q in primitive_types:
            if primitive_types[p] == primitive_types[q]:
                add_set(same_type, p, BasicPrimitive(q))
    sub_programs = set()
    
    for q in mutate_II_brutal(p, same_type, sub_programs, alpha, theta):
        yield q