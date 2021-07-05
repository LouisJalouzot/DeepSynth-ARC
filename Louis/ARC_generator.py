from copy import Error
from ARC.ARC_split import *
from dsl import *
from cfg import *
from pcfg import *
from Algorithms.heap_search import *
from Algorithms.bfs import *
from ARC.objects import *
from ARC.ARC import *
from sols import *

import pickle, json, copy

dsl_DS = DSL(DS_semantics, DS_primitive_types)
dsl_paperwork = DSL(paperwork_semantics, paperwork_primitive_types)
dsl = DSL(semantics, primitive_types)
set_types = dsl_DS.instantiate_polymorphic_types(10, True)
forced_types = {OBJ, COORD, COLOR}
# print(set_types)




##### Difficulty 1 #####
max_program_depth = 3
def generate():
    pcfgs = {}
    cfgs = {}
    for type_ in set_types:
        try:
            type_request = Arrow(OBJ, type_)
            pcfg = dsl_DS.DSL_to_Random_PCFG(type_request, max_program_depth=max_program_depth, forced_types=forced_types)
            pcfgs[type_request] = pcfg
        except:
            print("Impossible green type :", type_)
    
    for type1 in pcfgs:
        for type2 in pcfgs:
            # for type3 in pcfgs:
            try:
                type_request = Arrow(type1, Arrow(type2, Arrow(List(OBJ), List(OBJ))))
                # print(type_request)
                cfg = dsl_paperwork.DSL_to_Random_PCFG(type_request, max_program_depth=max_program_depth, forced_types=forced_types)
                # print(len(cfg.rules))
                cfgs[type1, type2] = cfg
            except:
                print("Impossible red type : {} -> {}".format(type1, type2))
    
    with open('ARC_testing/diff_I_data.pickle', 'wb') as f:
        data = pcfgs, cfgs
        pickle.dump(data, f)

# generate()
    
def diff_I():
    with open('ARC_testing/diff_I_data.pickle', 'rb') as f:
        pcfgs, cfgs = pickle.load(f)

    with open('ARC/data/training/a61ba2ce.json') as json_file: #1cf80156 3de23699
        pb = json.load(json_file)
        objects = find_objects(pb['train'][0]['input'])
        display(objects_to_grid(objects))
        # pb_ans = {}
        # pb_ans['train'] = [p_1cf80156.eval(dsl, (find_objects(pb['train'][i]['input']), None), p_1cf80156.hash+i) for i in range(3)]
        # pb_ans['test'] = p_1cf80156.eval(dsl, (find_objects(pb['test'][0]['input']), None), p_1cf80156.hash+3)
        # display(objects_to_grid(p_1cf80156.eval(dsl, (find_objects(pb['train'][0]['input']), None), p_1cf80156.hash)))
        # display(objects_to_grid(p_1cf80156.eval(dsl, (find_objects(pb['train'][1]['input']), None), p_1cf80156.hash+1)))
        # display(objects_to_grid(p_1cf80156.eval(dsl, (find_objects(pb['train'][2]['input']), None), p_1cf80156.hash+2)))
        # display(objects_to_grid(p_1cf80156.eval(dsl, (find_objects(pb['test'][0]['input']), None), p_1cf80156.hash+3)))
        # plt.show()

    good, bad = 0, 0
    for type1, type2 in cfgs:
        k = 0
        # print("TYPE1 : {}\nTYPE2 : {}\n".format(type1, type2))
        for p1 in bfs(cfgs[type1, type2]):
            k += 1
            if k > 5:
                break
            # print(p1)
            # p1 : (obj -> t1) -> (obj -> t2) -> list obj -> list obj
            p1 = reconstruct_from_compressed(p1, List(OBJ))
            for _ in range(1):
                # p2 : obj -> t1
                p2 = heap_search(pcfgs[type1]).__next__()
                # p3 : obj -> t2
                p3 = heap_search(pcfgs[type2]).__next__()
                assembled_program = Function(Lambda(Lambda(p1)), [Lambda(p2), Lambda(p3)])                       
                try:
                    # for i in range(3):
                    #     grid = pb['train'][i]['input']
                    #     res = assembled_program.eval(dsl, (find_objects(grid), None), assembled_program.hash+i)
                    #     if res != pb_ans['train'][i]:
                    #         raise Error
                    # print(assembled_program)
                    res = assembled_program.eval_naive(dsl, (copy.deepcopy(objects), None))
                    # print(assembled_program)
                    # print(res)
                    res = objects_to_grid(res)
                    good += 1
                    # if good % 1000 == 0:
                        # print(assembled_program)
                        # display(res)
                except:
                    print(assembled_program)
                    bad += 1

    print("good : {}\nbad : {}\nPercentage : {}%".format(good, bad, int(100 * good / (good + bad))))
    plt.show()


diff_I()


# cfg = dsl_paperwork.DSL_to_Random_PCFG(Arrow(Arrow(OBJ, Arrow(OBJ, INT)), Arrow(Arrow(OBJ, Arrow(OBJ, INT)), Arrow(List(OBJ), List(OBJ)))), forced_types={OBJ})
# sub_type = Arrow(OBJ, Arrow(COORD, OBJ))
# cfg = dsl_paperwork.DSL_to_Random_PCFG(Arrow(sub_type, Arrow(sub_type, Arrow(sub_type, Arrow(List(OBJ), List(OBJ))))), forced_types={OBJ, COORD, COLOR})
# print(len(cfg.rules))
# for _ in range(50):
#     print(bfs(cfg).__next__())