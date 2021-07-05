from sols import *
from dsl import *
from program import *
from ARC.objects import *
import json

def mutate_rec(l, f, l_args, i, n):
    if i == 0:
        # print("i == 0 : ", [[a] for a in l_args[i]])
        return [[a] for a in l_args[i]]
    elif i == n:
        for args in mutate_rec(l, f, l_args, i-1, n):
            # print("ARGS : ", args)
            l.append(Function(f, args))
    else:
        aux = []
        # print(l_args[i])
        # print(mutate_rec(l, f, l_args, i-1, n))
        for mutants_arg in mutate_rec(l, f, l_args, i-1, n):
            for a in l_args[i]:
                aux.append(mutants_arg+[a])
        # print("AUX : ", aux)
        return aux

def mutate(s, same_type):
    if isinstance(s, BasicPrimitive):
        return list(same_type[s.primitive])
    elif isinstance(s, Variable):
        return [Variable(i) for i in range(s.variable + 1)]
    elif isinstance(s, Lambda):
        return [Lambda(p) for p in mutate(s.body, same_type)]
    elif isinstance(s, Function):
        # print("S : ", s)
        l = []
        n = len(s.arguments)
        # print("S :", s)
        mutate_args = [mutate(arg, same_type) for arg in s.arguments]
        # print("mutate_args : ", mutate_args)
        for f in mutate(s.function, same_type):
            mutate_rec(l, f, mutate_args, n, n)
        return l
    return []

def mutation(semantics, primitive_types, pb, sol):
    dsl = DSL(semantics, primitive_types)
    same_type = {p: set() for p in primitive_types}
    for p in primitive_types:
        for q in primitive_types:
            if primitive_types[p] == primitive_types[q]:
                same_type[p].add(BasicPrimitive(q))

    mutants = mutate(sol, same_type)
    generated = []
    for mutant in mutants:
        try:
            new_pb = {}
            for mode in pb:
                new_pb[mode] = []
                for pair in pb[mode]:
                    ans = mutant.eval(dsl, (find_objects(pair['input']), None), p.__hash__)
                    new_pb[mode].append({'input': pair['input'], 'output': objects_to_grid(ans)})
            generated.append((new_pb, mutant))
        except:
            # print("Error eval")
            ()

    return generated

from ARC.ARC import semantics, primitive_types

with open('ARC/data/training/a87f7484.json') as json_file:
    pb = json.load(json_file)
    print("SOL : ", p_d364b489_aux)
    print(len(mutation(semantics, primitive_types, pb, p_d364b489_aux)))
    # for (pb, sol) in mutation(semantics, primitive_types, pb, p_a87f7484):
    #     print(sol)