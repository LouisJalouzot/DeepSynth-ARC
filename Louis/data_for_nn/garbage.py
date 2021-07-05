import pickle

with open('data_for_nn/cohesion_types.pickle', 'rb') as f:
    cohesion_types = pickle.load(f)
    
print(len(cohesion_types))