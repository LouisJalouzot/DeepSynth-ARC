import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
cmap = colors.ListedColormap(['#000', '#0074D9', '#FF4136', '#2ECC40', '#FFDC00', '#AAAAAA', '#F012BE', '#FF851B', '#7FDBFF', '#870C25'])
norm = colors.Normalize(0, 9)

file_name = 'data/training/681b3aeb.json' # sys.argv[1]

from ARC.objects import *

def main(file_name):
    with open('ARC/data/training/'+file_name) as json_file:
        pb = json.load(json_file)
        train = pb['train']
        test = pb['test']
        n = len(train)
        fig, plots = plt.subplots(n, 5)
        fig.suptitle('Problème ' + file_name)
        for i in range(n):
            plots[i][0].invert_yaxis()
            # print(train[i]['input'])
            plots[i][0].pcolormesh(train[i]['input'], cmap=cmap, norm=norm, edgecolor='xkcd:dark gray', linewidth=.01)
            plots[i][0].set_title('Example {} : input'.format(i+1))
            plots[i][1].invert_yaxis()
            plots[i][1].pcolormesh(train[i]['output'], cmap=cmap, norm=norm, edgecolor='xkcd:dark gray', linewidth=.01)
            plots[i][1].set_title('output')
            for j in range(5):
                plots[i][j].axis('off')
        n = len(test)
        for i in range(n):
            plots[i][3].invert_yaxis()
            plots[i][3].pcolormesh(test[i]['input'], cmap=cmap, norm=norm, edgecolor='xkcd:dark gray', linewidth=.01)
            plots[i][3].set_title('Test {} : input'.format(i+1))
            plots[i][4].invert_yaxis()
            plots[i][4].pcolormesh(test[i]['output'], cmap=cmap, norm=norm, edgecolor='xkcd:dark gray', linewidth=.01)
            plots[i][4].set_title('solution')
        # print(train)
        plt.show()

# main('c909285e.json')


def test_objects():
    with open(file_name) as json_file:
            pb = json.load(json_file)
            grid = pb['train'][1]['output']
            _, ax = plt.subplots(1)
            ax.invert_yaxis()
            ax.pcolormesh(grid, cmap=cmap, norm=norm, edgecolor='xkcd:dark gray', linewidth=.01)
            ax.set_title('Entry grid')
            for obj in find_objects(grid, cohesion_type='contact by point and color'):
                obj.display('display')

# test_objects()

#plt.savefig('figures/'+file_name[9:-5]+'.pdf')
# plt.show()