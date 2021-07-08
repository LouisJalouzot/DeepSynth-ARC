import json, pickle

def pickle_read(filename):
    with open(filename, 'rb') as f:
        ret = pickle.load(f)
    return ret

def pickle_write(filename, data):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

def json_read(filename):
    with open(filename, 'r') as f:
        ret = json.load(f)
    return ret

def json_write(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)