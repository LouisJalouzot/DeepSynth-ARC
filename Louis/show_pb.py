import matplotlib.pyplot as plt
from misc import *
from ARC.objects import *
from grids import *

l = pickle_read('data_for_nn/problems/diff_I_5_1000.pickle')
i = 0
for pb, p, c_type in l:
    if i % 5 == 0:
        display_pb(pb, 'Solution : '+str(p)+'\nCohesion type : '+cohesion_types_corresp[c_type])
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()
        plt.show(block=False)
        if input() == '0':
            break
        plt.close('all')
    i += 1
    
mut_l = pickle_read('data_for_nn/problems/mutation_10mutants_1grid.pickle')
for pb, p, c_type in mut_l:
    display_pb(pb, 'Solution : '+str(p)+'\nCohesion type : '+str(c_type))
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show(block=False)
    if input() == '0':
        break
    plt.close('all')