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

def mutate_list(l, i, n, same_type):
    if i == n:
        raise StopIteration
    else:
        for p in mutate(l[i], same_type):
            if i >= n - 1:
                l[i] = p
                yield None
            else:
                for _ in mutate_list(l, i+1, n, same_type):
                    l[i] = p
                    yield None

def mutate(p, same_type):
    if isinstance(p, BasicPrimitive):
        for q in same_type[p.primitive]:
            yield q
    elif isinstance(p, Variable):
        for i in range(p.variable + 1):
            yield Variable(i)
    elif isinstance(p, Lambda):
        for q in mutate(p.body, same_type):
            yield Lambda(q)
    elif isinstance(p, Function):
        for f in mutate(p.function, same_type):
            for _ in mutate_list(p.arguments, 0, len(p.arguments), same_type):
                yield Function(f, p.arguments)
    return []

def program_generator(primitive_types, sol):
    same_type = {p: set() for p in primitive_types}
    for p in primitive_types:
        for q in primitive_types:
            if primitive_types[p] == primitive_types[q]:
                same_type[p].add(BasicPrimitive(q))
                
    for p in mutate(sol, same_type):
        yield p




def build_aux(pb, p, objects, output, b_color=0):
    new_pb = {'train': [], 'test': []}
    for mode in objects:
        for i in range(len(objects[mode])):
            new_pb[mode].append({})
            res = p.eval_naive(dsl, (objects[mode][i]['input'], None))
            if output == 'grids':
                new_pb[mode][i]['input'] = pb[mode][i]['input']
                new_pb[mode][i]['output'] = objects_to_grid(res, background_color=b_color)
            else:
                new_pb[mode][i]['input'] = objects[mode][i]['input']
                new_pb[mode][i]['output'] = res
    return new_pb, p

def build_aux_aux(pb, p, output):
    new_pb = {'train': [], 'test': []}
    for mode in pb:
        for objects, n in pb[mode]:
            new_pb[mode].append({})
            res = p.eval_naive(dsl, (objects, None))
            if output == 'grids':
                new_pb[mode][-1]['input'] = objects_to_grid(objects, n, n)
                new_pb[mode][-1]['output'] = objects_to_grid(res)
            else:
                new_pb[mode][-1]['input'] = objects
                new_pb[mode][-1]['output'] = res
    return new_pb, p

def build_mutation_pb(size_per_sol=1000, nb_grids=10, output='grids'):
    for name in solutions:
        i = 0
        pb = json_read('ARC/data/training/'+name)
        objects = {'train': [], 'test': []}
        for mode in pb:
            for pair in pb[mode]:
                objects[mode].append({'input': find_objects(pair['input'], cohesions[name], background_color[name])})
        for p in program_generator(primitive_types, solutions[name]):
            i += 1
            if i > size_per_sol:
                break
            try:
                new_pb, p = build_aux(pb, p, copy.deepcopy(objects), output, background_color[name])
                yield new_pb, p
            except:
                try:
                    j = 0
                    for new_pb, _ in grid_generator(output='objects'):
                        j += 1
                        if j > nb_grids:
                            break
                        try:
                            yield build_aux_aux(new_pb, p, output)
                            break
                        except:
                            pass
                except:
                    pass


# i = 0
# for pb, p in build_mutation_pb(200):
#     i += 1
#     if i % 50 == 0:
#         print(p)
#         display_pb(pb)
#         plt.show(block=False)
#         if input() == '0':
#             break
#         plt.close()

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
        
def generate_II_brutal(p, same_type, sub_programs, alpha=0.5, theta=0.2):
    same_type = {}
    for p in primitive_types:
        for q in primitive_types:
            if primitive_types[p] == primitive_types[q]:
                add_set(same_type, p, BasicPrimitive(q))
    sub_programs = set()
    
    for q in mutate_II_brutal(p, same_type, sub_programs, alpha, theta):
        yield q