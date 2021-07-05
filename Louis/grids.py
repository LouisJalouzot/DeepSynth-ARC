import sys, copy, matplotlib.pyplot as plt, json, pickle
sys.path.insert(0, '..')

from Louis.ARC.objects import *
from Louis.ARC.main import *
import pathlib, pickle, json

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

with open('data_for_nn/pb_names.json', 'r') as f:
    names = json.load(f)

with open('data_for_nn/cohesion_types.json', 'r') as f:
    cohesion_types = json.load(f)
    
print(len(cohesion_types))

for name in names[len(cohesion_types):]:
    main(name)
    plt.show(block = False)
    try:
        a = int(input())
        if a not in cohesion_types_corresp: raise TypeError
        cohesion_types[name] = a
    except:
        break
    plt.close()

with open('data_for_nn/cohesion_types.json', 'w') as f:
    json.dump(cohesion_types, f)