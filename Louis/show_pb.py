import matplotlib.pyplot as plt, sys
sys.path.insert(0, '..')
from Louis.misc import *
from Louis.ARC_data.objects import *
from Louis.grids import *
from Louis.unifying import *
    
def show_pb(name, n=17):
    l, i = reversed(pickle_read(name)), 0
    for pb, p, c_type in l:
        i += 1
        if i % n == 0:
            print(p)
            pb_to_grid(pb)
            display_pb(pb, 'Solution : '+str(p)+'\nCohesion type : '+str(c_type))
            # figManager = plt.get_current_fig_manager()
            # figManager.window.showMaximized()
            plt.show(block=False)
            if input() == '0': break
            plt.close('all')

if __name__ == '__main__':
    show_pb('../../espace partage remy louis/Louis/mutation.pickle', 1)
    # l = pickle_read('../../espace partage remy louis/Louis/mutation.pickle')
    # ans = [0] * 11
    # i = 0
    # j = 0
    # for _, p, _ in l:
    #     if contains(p, 'singleton'): i += 1
    #     if contains(p, 'car'): j += 1
    #     _, d = analyze_var(p)
    #     ans[d] += 1
    # print(ans, i, j)
    
# l = pickle_read('../../espace partage remy louis/diff_I_rand_5_25_10000.pickle')





# l = pickle_read('data_for_nn/problems/diff_I_5_1000.pickle')
# i = 0
# for pb, p, c_type in l:
#     if i % 5 == 0:
#         display_pb(pb, 'Solution : '+str(p)+'\nCohesion type : '+cohesion_types_corresp[c_type])
#         figManager = plt.get_current_fig_manager()
#         figManager.window.showMaximized()
#         plt.show(block=False)
#         if input() == '0':
#             break
#         plt.close('all')
#     i += 1
    
# mut_l = pickle_read('data_for_nn/problems/mutation_10mutants_1grid.pickle')
# for pb, p, c_type in mut_l:
#     display_pb(pb, 'Solution : '+str(p)+'\nCohesion type : '+str(c_type))
#     figManager = plt.get_current_fig_manager()
#     figManager.window.showMaximized()
#     plt.show(block=False)
#     if input() == '0':
#         break
#     plt.close('all')