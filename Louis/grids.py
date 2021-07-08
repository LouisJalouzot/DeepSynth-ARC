import sys, copy, matplotlib.pyplot as plt, json, pickle, numpy as np, random
sys.path.insert(0, '..')

from Louis.misc import *
from Louis.ARC.objects import *
from Louis.ARC.main import *
import pathlib, pickle, json, vose

cohesion_types_corresp = {
    1: 'contact',
    2: 'contact by point',
    3: 'contact and color',
    4: 'contact by point and color',
    5: 'color',
    6: 'skip'
}

# all_training_problems = []
# for path in pathlib.Path('ARC/data/training').iterdir():
#     all_training_problems.append(str(path).split('/')[-1])

# with open('data_for_nn/pb_names.pickle', 'wb') as f:
#     pickle.dump(all_training_problems, f)

names = json_read('data_for_nn/pb_names.json')
cohesion_types = json_read('data_for_nn/cohesion_types.json')

################################################################ Classification cohesion types for each pb
# print(len(cohesion_types))
# start = names.index(list(cohesion_types.keys())[-1]) + 1
# print("To go :", len(names)-start)
# for i in range(start, len(names)):
#     name = names[i]
#     main(name)
#     plt.show(block = False)
#     try:
#         a = int(input())
#         if a not in cohesion_types_corresp: raise TypeError
#         cohesion_types[name] = a
#     except:
#         break
#     plt.close()

# with open('data_for_nn/cohesion_types.json', 'w') as f:
#     json.dump(cohesion_types, f)


################################################################ Récolte des objets
# list_objects_contact = []
# list_objects_contact_point = []
# list_objects_contact_color = []
# list_objects_contact_point_color = []
# list_objects_color = []

# repartition = [0] * 104
# for name in cohesion_types:
#     c_type = cohesion_types_corresp[cohesion_types[name]]
#     print(name)
#     with open('ARC/data/training/'+name, 'r') as f:
#         pb = json.load(f)
#     for mode in pb:
#         for pair in pb[mode]:
#             repartition[len(find_objects(pair['input'], c_type))] += 1
#             # for io in pair:
#             #     if c_type == 'skip': break
#             #     elif c_type == 'contact':
#             #         list_objects_contact += find_objects(pair[io], c_type)
#             #     elif c_type == 'contact by point':
#             #         list_objects_contact_point += find_objects(pair[io], c_type)
#             #     elif c_type == 'contact and color':
#             #         list_objects_contact_color += find_objects(pair[io], c_type)
#             #     elif c_type == 'contact by point and color':
#             #         list_objects_contact_point_color += find_objects(pair[io], c_type)
#             #     elif c_type == 'color':
#             #         list_objects_color += find_objects(pair[io], c_type) 
    


# for i in range(5):
#     lists = [list_objects_contact, list_objects_contact_point, list_objects_contact_color, list_objects_contact_point_color, list_objects_color]
#     names = ['list_objects_contact', 'list_objects_contact_point', 'list_objects_contact_color', 'list_objects_contact_point_color', 'list_objects_color']
#     with open('data_for_nn/objects/'+names[i]+'.pickle', 'wb') as f:
#         pickle.dump(lists[i], f)


# for name in cohesion_types:
#     # print(name)
#     c_type = cohesion_types_corresp[cohesion_types[name]]
#     if c_type != 'contact' and c_type != 'contact by point':
#         pb = json_read('ARC/data/training/'+name)
#         for mode in pb:
#             for pair in pb[mode]:
#                 for obj in find_objects(pair['input'], c_type):
                    # if (obj.rectangle_size()[0] > 10 or obj.rectangle_size()[1] > 10) and obj.nb_points()/(obj.rectangle_size()[0]*obj.rectangle_size()[1]) < 0.5:
                    #     continue
                    # if obj.nb_points() > 86:
                    #     continue
                    # print("Density :", obj.nb_points()/(obj.rectangle_size()[0]*obj.rectangle_size()[1]))
                    #     obj.display()
                    #     plt.show(block=False)
                    #     input()
                    #     plt.close()
                
################################## Only dense objects
# l = pickle_read('data_for_nn/objects/list_objects_contact.pickle')
# l_aux = []
# for obj in l:
#     if (obj.rectangle_size()[0] > 10 or obj.rectangle_size()[1] > 10) and obj.nb_points()/(obj.rectangle_size()[0]*obj.rectangle_size()[1]) < 0.5:
#         continue
#     if obj.nb_points() > 86:
#         continue
#     l_aux.append(obj)
# print(len(l), len(l_aux))
# pickle_write('data_for_nn/objects/list_objects_contact_dense.pickle', l_aux)

        
# grid_size_distrib = [[0] * 31 for _ in range(31)]
# nb_pb_same_size_grid_entry = 0
# for name in cohesion_types:
#     pb = json_read('ARC/data/training/'+name)
#     for mode in pb:
#         for pair in pb[mode]:
#                 n, m = np.array(pair['input']).shape
#                 nb_pb_same_size_grid_entry += 1
#                 grid_size_distrib[n][m] += 1

# print(nb_pb_same_size_grid_entry)
# for i in range(31):
#     for j in range(31):
#         grid_size_distrib[i][j] /= nb_pb_same_size_grid_entry
# json_write('data_for_nn/objects/distrib_grid_size.json', grid_size_distrib)

def choice(p):
    x = np.random.rand()
    cum = 0
    for i, p in enumerate(p):
        cum += p
        if x < cum:
            return i
    return -1

def sanity_check(c_type, grid, i, j, c, n, background_color = 0):
    if c_type > 4:
        return False
    
    if i > 0:
        if grid[i-1][j] == c:
            return True
        if (c_type == 1 or c_type == 2) and grid[i-1][j] != background_color:
            return True
    if j > 0:
        if grid[i][j-1] == c:
            return True
        if (c_type == 1 or c_type == 2) and grid[i][j-1] != background_color:
            return True
    if i+1 < n:
        if grid[i+1][j] == c:
            return True
        if (c_type == 1 or c_type == 2) and grid[i+1][j] != background_color:
            return True
    if j+1 < n:
        if grid[i][j+1] == c:
            return True
        if (c_type == 1 or c_type == 2) and grid[i][j+1] != background_color:
            return True
    
    if i > 0 and j > 0:
        if c_type == 2 and grid[i-1][j-1] != background_color:
            return True
        if c_type == 4 and grid[i-1][j-1] == c:
            return True
    if i+1 < n and j+1 < n:
        if c_type == 2 and grid[i+1][j+1] != background_color:
            return True
        if c_type == 4 and grid[i+1][j+1] == c:
            return True
    return False

def grid_generator(tries = 100, background_color = 0):
    cohesions_sampler = vose.Sampler(np.array([0, 26, 10, 53, 26, 33]) / 148)
    nb_ex_sampler = vose.Sampler(np.array([0, 19, 83, 30, 9]) / 141)
    nb_objects_sampler = vose.Sampler(np.array(json_read('data_for_nn/objects/distrib_nb_obj.json')))
    size_objects_sampler = vose.Sampler(np.array(json_read('data_for_nn/objects/distrib_size_obj.json')))
    lists_objects = pickle_read('data_for_nn/objects/lists_obj_dense.pickle')
    nb_obj = [[len(l_) for l_ in l] for l in lists_objects]
    size_grid_sampler = vose.Sampler(np.array([sum(l) for l in json_read('data_for_nn/objects/distrib_grid_size.json')]))
    size_grid_constant_sampler = vose.Sampler(np.array([sum(l) for l in json_read('data_for_nn/objects/distrib_grid_size_constant.json')]))
    while True:
        pb = {'train': [], 'test': []}
        ex = nb_ex_sampler.sample()
        if np.random.randint(2) == 1:
            n = size_grid_constant_sampler.sample()
            pb['test'].append({'input': np.zeros((n, n))})
            for _ in range(ex):
                pb['train'].append({'input': np.zeros((n, n))})
        else:
            n = size_grid_sampler.sample()
            pb['test'].append({'input': np.zeros((n, n))})
            for _ in range(ex):
                n = size_grid_sampler.sample()
                pb['train'].append({'input': np.zeros((n, n))})
        
        c_type = cohesions_sampler.sample()
        for mode in pb:
            for pair in pb[mode]:
                n = len(pair['input'])
                nb = nb_objects_sampler.sample()
                colors_ = [0] * 10
                for _ in range(nb):
                    try_n = 0
                    while try_n < tries:
                        try_n += 1
                        k = size_objects_sampler.sample()
                        try:
                            ind = np.random.randint(nb_obj[c_type][k])
                            obj = lists_objects[c_type][k][ind]
                            if c_type == 5 and colors_[obj.color] == 1:
                                raise StopIteration
                            if c_type == 5:
                                colors_[obj.color] = 1
                            a, b = obj.rectangle_size()
                            if a > n or b > n:
                                raise StopIteration
                            x, y = np.random.randint(0, n - a), np.random.randint(0, n - b)
                            for i, j, c in obj.points:
                                if pair['input'][i + x][j + y] != background_color:
                                    raise StopIteration
                                if sanity_check(c_type, pair['input'], i + x, j + y, c, n):
                                    raise StopIteration
                            for i, j, c in obj.points:
                                pair['input'][i + x][j + y] = c
                            break
                        except:
                            pass
        
        for mode in pb:
            for pair in pb[mode]:
                pair['input'] = pair['input'].tolist()
        yield pb, c_type


i = 0
for pb in grid_generator():
    i += 1
    if i > 5000:
        break

# for pb, c_type in grid_generator():
#     print(cohesion_types_corresp[c_type])
#     for mode in pb:
#         for pair in pb[mode]:
#             display(pair['input'])
#     plt.show(block=False)
#     input()
#     plt.close()