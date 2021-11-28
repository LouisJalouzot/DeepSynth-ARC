import os, sys, random
sys.path.insert(0, '..')

hashseed = os.getenv('PYTHONHASHSEED')
if not hashseed:
    os.environ['PYTHONHASHSEED'] = '0'
    os.execv(sys.executable, [sys.executable] + sys.argv)

from Louis.ARC_data.ARC import *
from program import *
from Louis.solutions import *
from Louis.mutation import *
from Louis.ARC_generator import *
from Louis.grids import *

original_primitive_types = copy.deepcopy(primitive_types)
fresh_var, sub_prog, pb_unif, subst = 0, set(), [], {}
max_d_col = 5

def contains(p, s):
    if isinstance(p, BasicPrimitive): return p.primitive == s
    elif isinstance(p, Lambda): return contains(p.body, s)
    elif isinstance(p, Function): return contains(p.function, s) or any(contains(arg, s) for arg in p.arguments)
    else: return False

def pruned_env(env, l, i=0):
    if l == [] or env == None or i > l[0]: return None
    elif i == l[-1]:
        t, env = env
        l.pop()
        return t, pruned_env(env, l, i+1)
    else:
        _, env = env
        return None, pruned_env(env, l, i+1)

def analyze_var(p, lambda_depth=0):
    if isinstance(p, Variable):
        if p.variable < lambda_depth: return set(), 1
        else: return {p.variable}, 1
    if isinstance(p, Lambda):
        list_var, depth = analyze_var(p.body, lambda_depth+1)
        return {x-1 for x in list_var}, depth
    if isinstance(p, Function):
        list_var, f_depth = analyze_var(p.function, lambda_depth)
        arg_depth = -1
        for arg in p.arguments:
            l, d = analyze_var(arg, lambda_depth)
            list_var |= l
            arg_depth = max(arg_depth, d)
        return list_var, max(arg_depth + 1, f_depth)
    return set(), 1

class EnhancedProgram(Program):
    def __init__(self, p, env, type):
        self.p = copy.deepcopy(p)
        list_var, depth = analyze_var(p)
        self.depth = depth
        self.list_var = list_var
        self.env_types = pruned_env(env, sorted(list_var, reverse=True))
        self.type = type
        self.end_type = None
        self.in_types = None
    
    def __eq__(self, other): return self.p == other.p and self.env_types == other.env_types
    def __hash__(self): return hash((self.p.hash, hash(self.env_types)))
    def __repr__(self): return format(self.env_types)+'|- '+format(self.p)+': '+format(self.type)

def pb_unif_gen(p, env=(List(OBJ), None), dont_add=False):
    global fresh_var, sub_prog, pb_unif
    if isinstance(p, Variable): new_t = index(env, p.variable)
    elif isinstance(p, BasicPrimitive): new_t = primitive_types[p.primitive]
    elif isinstance(p, Lambda):
        new_poly = PolymorphicType(str(fresh_var))
        fresh_var += 1
        t = pb_unif_gen(p.body, (new_poly, env))
        new_t = Arrow(new_poly, t)
    elif isinstance(p, Function):
        l_t = reversed([pb_unif_gen(arg, env) for arg in p.arguments])
        new_t = PolymorphicType(str(fresh_var))
        arr = new_t
        fresh_var += 1
        new_env = env
        for t_arg in l_t:
            arr = Arrow(t_arg, arr)
            new_env = (t_arg, new_env)
        t_fun = pb_unif_gen(p.function, new_env)
        pb_unif.append((t_fun, arr))
    if not isinstance(p, Lambda) and not isinstance(p, Variable) and not dont_add:
        p_e = EnhancedProgram(p, env, new_t)
        if p_e.depth < max_d_col: sub_prog.add(p_e)
    return new_t

def appears(t, t_):
    if isinstance(t_, PolymorphicType): return t == t_
    if isinstance(t_, List): return appears(t, t_.type_elt)
    if isinstance(t_, Arrow): return appears(t, t_.type_in) or appears(t, t_.type_out)
    return False

def unify():
    global fresh_var, sub_prog, pb_unif, subst
    if pb_unif == []: return True
    t, t_ = pb_unif.pop()
    if t == t_: return unify()
    if isinstance(t, PolymorphicType) and isinstance(t_, PolymorphicType):
        if t in subst and t_ in subst: pb_unif.append((subst[t], subst[t_]))
        elif t in subst: pb_unif.append((subst[t], t_))
        elif t_ in subst: pb_unif.append((t, subst[t_]))
        else: subst[t] = t_
        return unify()
    if isinstance(t, PolymorphicType):
        if appears(t, t_): raise Exception('Not unifyable: {} appears in {}'.format(t, t_))
        if t in subst: pb_unif.append((subst[t], t_))
        else: subst[t] = t_
        return unify()
    elif isinstance(t_, PolymorphicType):
        if appears(t_, t): raise Exception('Not unifyable: {} appears in {}'.format(t_, t))
        if t_ in subst: pb_unif.append((t, subst[t_]))
        else: subst[t_] = t
        return unify()
    elif isinstance(t, Arrow) and isinstance(t_, Arrow):
        pb_unif.append((t.type_in, t_.type_in))
        pb_unif.append((t.type_out, t_.type_out))
        return unify()
    elif isinstance(t, List) and isinstance(t_, List):
        pb_unif.append((t.type_elt, t_.type_elt))
        return unify()
    raise Exception('Not unifyable: {} == {}'.format(t_, t))

def replace(t, corresp):
    global fresh_var
    if isinstance(t, PolymorphicType):
        if t not in corresp:
            corresp[t] = PolymorphicType(str(fresh_var))
            fresh_var += 1
        return corresp[t]
    elif isinstance(t, List): return List(replace(t.type_elt, corresp))
    elif isinstance(t, Arrow): return Arrow(replace(t.type_in, corresp), replace(t.type_out, corresp))    
    return t

def replace_subst(t):
    global subst
    if isinstance(t, PolymorphicType): ans = replace_subst(subst[t])
    elif isinstance(t, List): ans = List(replace_subst(t.type_elt))
    elif isinstance(t, Arrow): ans = Arrow(replace_subst(t.type_in), replace_subst(t.type_out))
    else: ans = t
    subst[t] = ans
    return ans

def replace_subst_env(env):
    global subst
    if env == None: return env
    t, env = env
    return replace_subst(t), replace_subst_env(env)

def unify_mut(p, type_request=Arrow(List(OBJ), List(OBJ)), dont_add=False):
    global fresh_var, sub_prog, pb_unif, subst
    fresh_var, sub_prog, pb_unif, subst = 0, set(), [], {}
    for primitive in primitive_types: primitive_types[primitive] = replace(primitive_types[primitive], {})
    t = pb_unif_gen(p, (type_request.type_in, None), dont_add=dont_add)
    pb_unif.append((t, type_request.type_out))
    try: unify()
    except Exception: return
    for p_e in sub_prog:
        p_e.type = replace_subst(p_e.type)
        p_e.env_types = replace_subst_env(p_e.env_types)
    return sub_prog

def env_to_list(env, acc):
    if env == None: return acc
    t, new_env = env
    acc.append(t)
    return env_to_list(new_env, acc)

def new_constraints(env1, env2, i):
    k = min(len(env1), len(env2) - i)
    for j in range(k):
        t1, t2 = env1[j], env2[i + j]
        if t1 != None and t2 != None and t1 != t2: return False, None, None
    for j in range(k):
        t1, t2 = env1[j], env2[i + j]
        if t2 == None: env2[i + j] = t1
        elif t1 == None: env1[j] = t2
    return True, env1[k:], env2

def compare_end_env(env1, env2): # need to be reversed list env
    if env1 == [] or env2 == []: return env1, env2
    for i in range(len(env2)):
        b, new_env1, new_env2 = new_constraints(env1, env2, i)
        if b: return list(reversed(new_env1)), list(reversed(new_env2))
    return list(reversed(env1)), list(reversed(env2))

def end_type(t):
    if isinstance(t, Arrow): return end_type(t.type_out)
    return t

def gen_data_sample(nb_mutants=0):
    global subst
    sub_prog_glob = set()
    for name in solutions:
        ans = unify_mut(solutions[name], dont_add=True)
        if ans != None: sub_prog_glob |= ans
    sub_prog_aux = set()
    for e_p in sub_prog_glob:
        i = 0
        for p in mutate(e_p.p):
            i += 1
            if i > nb_mutants: break
            new_e_p = EnhancedProgram(p, e_p.env_types, e_p.type)
            sub_prog_aux.add(new_e_p)
    sub_prog_glob |= sub_prog_aux
    end_types = {}
    for p_e in sub_prog_glob:
        t = end_type(p_e.type)
        p_e.end_type = t
        p_e.in_types = p_e.type.ends_with(t)
        p_e.env_types = env_to_list(p_e.env_types, [])
        if t in end_types:
            end_types[t]['programs'].append(p_e)
            end_types[t]['nb'] += 1
        else: end_types[t] = {'programs': [p_e], 'nb': 1}
    prim_set = set()
    for t in end_types.keys():
        for t_ in end_types.keys():
            subst = {t0: t, t1: t_}
            for primitive in original_primitive_types: prim_set.add((primitive, replace_subst(original_primitive_types[primitive])))
    for p, t in prim_set:
        p_e = EnhancedProgram(BasicPrimitive(p), None, t)
        end_t = end_type(t)
        p_e.end_type = end_t
        p_e.in_types = t.ends_with(end_t)
        p_e.env_types = env_to_list(p_e.env_types, [])
        if end_t in end_types:
            end_types[end_t]['programs'].append(p_e)
            end_types[end_t]['nb'] += 1
        else: end_types[end_t] = {'programs': [p_e], 'nb': 1}
    for t in end_types:
        for i in range(3):
            p_e = EnhancedProgram(Variable(i), None, t)
            p_e.in_types = []
            p_e.env_types = [None] * i + [t]
            end_types[t]['programs'].append(p_e)
            end_types[t]['nb'] += 1
    pickle_write('data_for_nn/end_types.pickle', end_types)
  
def sample_mutate(end_types, type_request, env, poly_corresp, depth=0, depth_max=10):
    if depth > depth_max: raise Exception('Too deep')
    if type_request == None: raise Exception('Unused variable')
    if isinstance(type_request, Arrow):
        t_in, t_out = type_request.type_in, type_request.type_out
        p = sample_mutate(end_types, t_out, (t_in, env), poly_corresp, depth)
        return Lambda(p)
    if isinstance(type_request, PolymorphicType):
        if type_request not in poly_corresp: poly_corresp[type_request] = random.choice(end_types.keys())
        type_request = poly_corresp[type_request]
    memory_corresp = copy.deepcopy(poly_corresp)
    ind = random.randrange(end_types[type_request]['nb'])
    p_e = end_types[type_request]['programs'][ind]
    while isinstance(p_e.p, Variable) and p_e.p.variable >= len(env):
        ind = random.randrange(end_types[type_request]['nb'])
        p_e = end_types[type_request]['programs'][ind]
    env1, env2 = compare_end_env(p_e.env_types, env)
    l_arg = [sample_mutate(end_types, t_arg, env2, poly_corresp, depth+1) for t_arg in p_e.in_types]
    p = Function(p_e.p, l_arg)
    l_env = []
    for t_env in env1:
        l_env.append(sample_mutate(end_types, t_env, env1, poly_corresp, depth+1))
        p = Lambda(p)
    poly_corresp = memory_corresp
    if l_env == []: return p
    else: return Function(p, l_env)
         
def sample_mutate_glob(type_request=List(OBJ), env=[List(OBJ)], depth_min=3, depth_max=10):
    end_types = pickle_read('data_for_nn/end_types.pickle')
    # i = 0
    # for t in end_types:
    #     print("#####", t)
    #     for p_e in end_types[t]['programs']:
    #         i += 1
    #         print(p_e)
    # print(i)
    i = 0
    while True:
        try:
            p = sample_mutate(end_types, type_request, env, {}, depth_max=depth_max)
            d = program_depth(p)
            if contains(p, 'singleton'):
                if random.random() > .01: raise Exception
            if d == depth_min :
                if random.random() > .5: raise Exception
            if depth_max >= d >= depth_min:
                yield p, i
                i = 0
            else: i += 1
        except GeneratorExit: return
        except: i += 1
              
def mutate_pb_generator(grid_gen, grids_per_program=1, nb_grids=30, output='objects', watcher_limit=5):
    for p, _ in sample_mutate_glob():
        k, success = 0, 0
        watcher = {'Identity program': 0, 'Empty grid': 0, 'Objects overlap': 0}
        for pb, c_type in grid_gen:
            try:
                try_pb_p(dsl, p, pb)
                if output == 'grids': pb_to_grid(pb)
                yield pb, p, c_type
                success += 1
            except Exception as s:
                if format(s) in watcher:
                    watcher[format(s)] += 1
                    bad_program = None
                    for mis in watcher:
                        if watcher[mis] > watcher_limit: bad_program = mis
                    if bad_program != None: break
            if k > nb_grids or success > grids_per_program: break
            k += 1

if __name__ == "__main__":
    # gen_data_sample(100)
    # for data in sample_mutate_glob():
    #     print(data)
    #     if input() == '0': break
    # speed_test(sample_mutate_glob(), 1000)
    # speed_test(mutate_pb_generator(grid_generator_cor()), 500)
    i, n = 0, 10000
    l = []
    for pb, p, c_type in mutate_pb_generator(grid_generator()):
        i += 1
        if i > n: break
        l.append((pb, p, c_type))
        if (100 * i) % n == 0:
            print('{}%'.format(int(100*i/n)))
    pickle_write('../../espace partage remy louis/Louis/mutation_rand.pickle', l)
    #     display_pb(pb, format(p))
    #     figManager = plt.get_current_fig_manager()
    #     figManager.window.showMaximized()
    #     plt.show(block=False)
    #     if input() == '0': break
    #     plt.close('all')
    
    
    
    
################################ OLD
# def mutate_pb_generator(grid_gen, grids_per_program=1, nb_grids=10, output='grids'):
#     for p, _ in sample_mutate_glob():
#         k = 0
#         for pb, c_type in grid_gen:
#             k += 1
#             if k > nb_grids: break
#             try:
#                 for mode in pb:
#                     for pair in pb[mode]:
#                         objects, n, m = pair['input']
#                         res = p.eval_naive(dsl, (copy.deepcopy(objects), None))
#                         if res == objects: raise Exception('identity program')
#                         safe = False
#                         for obj in res:
#                             x, y = obj.low
#                             for i, j, c in obj.points:
#                                 if c != 0 and 0 <= i + x < 30 and 0 <= j + y < 30:
#                                     safe = True
#                                     break
#                             if safe:
#                                 break
#                         if not safe: raise Exception('empty grid')
#                         pair['output'] = res, n, m
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
#                 if not safe: raise Exception('constant progam')
#                 if output == 'grids':
#                     for mode in pb:
#                         for pair in pb[mode]:
#                             for io in pair:
#                                 objects, n, m = pair[io]
#                                 pair[io] = objects_to_grid(objects, n, m, supple=(io=='output'))
#                 yield pb, p, c_type
#                 break
#             except Exception as s:
#                 if s == 'Empty': print(p)