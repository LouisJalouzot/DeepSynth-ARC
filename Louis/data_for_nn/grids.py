from ARC.objects import *
from ARC.main import *
import pathlib, pickle, json

cohesion_types_corresp = {1: 'contact',
                  2: 'contact by point',
                  3: 'contact and color',
                  4: 'contact by point and color',
                  5: 'color',
                  6: 'skip'}

# all_training_problems = []
# for path in pathlib.Path('ARC/data/training').iterdir():
#     all_training_problems.append(str(path).split('/')[-1])

# with open('data_for_nn/pb_names.pickle', 'wb') as f:
#     pickle.dump(all_training_problems, f)

with open('data_for_nn/pb_names.pickle', 'rb') as f:
    names = pickle.load(f)

with open('data_for_nn/cohesion_types.pickle', 'rb') as f:
    cohesion_types = pickle.load(f)
for name in names[50:60]:
    main(name)
    plt.show(block = False)
    try:
        cohesion_types[name] = input()
    except:
        break
    plt.close()

with open('data_for_nn/cohesion_types.pickle', 'wb') as f:
    pickle.dump(cohesion_types, f)
    