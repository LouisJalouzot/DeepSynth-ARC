import json
import numpy as np
import matplotlib.pyplot as plt
import sys

# proportion de la couleur passée en argument en moyenne dans les grilles d'entrée (training + test)

file_name = sys.argv[1]
color = int(sys.argv[2])

with open(file_name) as json_file:
    pb = json.load(json_file)
    train = pb['train']
    avg = 0
    for i in range(len(pb['test'])):
        train.append({'input': pb['test'][i]['input']})
    n = len(train)
    for k in range(n):
        c = 0
        grid = train[k]['input']
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == color :
                    c += 1
        avg += c / (len(grid) * len(grid[0]))
    print(avg/n)