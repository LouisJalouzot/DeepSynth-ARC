import torch, logging, os, sys, random
sys.path.insert(0, '..')
from torch import nn

from Louis.solutions import *
from Louis.misc import *
from Louis.grids import grid_generator_cor
from Louis.ARC_generator import appears, dsl

class Net(nn.Module):
    def __init__(self, primitive_types, nb_objects_max=10):
        super(Net, self).__init__()
        self.primitives = {p: i for i, p in enumerate(primitive_types.keys())}
        self.nb_primitives = len(self.primitives)
        self.nb_objects_max = nb_objects_max
        self.nb_channels = 2 * self.nb_objects_max
        self.fe = nn.Sequential( # (20, 30, 30)
            nn.Conv2d(self.nb_channels, self.nb_channels, 3), # (20, 28, 28)
            nn.Conv2d(self.nb_channels, self.nb_channels * 2, 3), # (40, 26, 26)
            nn.MaxPool2d(2), # (40, 13, 13)
            nn.Flatten(), # (6760)
        )
        self.input_dim = self.nb_channels * 2 * 13 * 13
        self.hidden_dim = self.nb_primitives * 10
        self.rnn = nn.RNN(input_size=self.input_dim, hidden_size=self.hidden_dim, nonlinearity='relu', batch_first=True)
        self.loss = torch.nn.MSELoss()
        self.fc = nn.Linear(self.hidden_dim, self.nb_primitives)
        
    def forward(self, embedded_tasks):
        h0 = torch.zeros(1, embedded_tasks.size(0), self.hidden_dim)
        out, _ = self.rnn(embedded_tasks, h0)
        return self.fc(out[:, -1, :])
    
    def embed_program_rec(self, tensor, p):
        if isinstance(p, BasicPrimitive):
            try: tensor[self.primitives[p.primitive]] = 1
            except: pass # not a domain specific primitive
        elif isinstance(p, Function):
            self.embed_program_rec(tensor, p.function)
            for arg in p.arguments: self.embed_program_rec(tensor, arg)
        elif isinstance(p, Lambda): self.embed_program_rec(tensor, p.body)
        
    def embed_program(self, p):
        tensor = torch.zeros(self.nb_primitives)
        self.embed_program_rec(tensor, p)
        return tensor
    
    def embed_all_programs(self, programs): return torch.stack([self.embed_program(p) for p in programs])

    def embed_list_obj(self, list_objects):
        objects = torch.zeros(self.nb_objects_max, 30, 30)
        for index, obj in enumerate(list_objects):
            if index >= self.nb_objects_max: break
            for i, j, c in obj.points:
                if 0 <= i + obj.low[0] < 30 and 0 <= j + obj.low[1] < 30 and 0 <= c <= 9:
                    objects[index, i + obj.low[0], j + obj.low[1]] = c
        return objects

    def embed_task(self, pb):
        res = []
        for pair in pb['train']:
            em_input = self.embed_list_obj(pair['input'][0])
            em_output = self.embed_list_obj(pair['output'])
            res.append(torch.cat([em_input, em_output]))
        return self.fe(torch.stack(res))

    def embed_all_tasks(self, tasks):
        return nn.utils.rnn.pad_sequence([self.embed_task(task) for task in tasks], batch_first=True)
    
    def train(self, batch_generator, epochs=200, lr=1e-4):
        optimizer = torch.optim.Adam(self.parameters(), lr=lr)
        for tasks, embedded_programs in batch_generator:
            for _ in range(epochs):
                optimizer.zero_grad()
                embedded_tasks = self.embed_all_tasks(tasks)
                nn_preds = self(embedded_tasks)
                loss_value = self.loss(nn_preds, embedded_programs)
                loss_value.backward()
                optimizer.step()
                yield loss_value.item()
                    
    def test(self, task, p=None, pb=None):
        nn_pred = self(self.embed_all_tasks([task]))[0]
        if pb != None:
            pb_to_grid(pb)
            display_pb(pb, format(p if p != None else ""))
            plt.show(block=False)
        if p != None:
            print(p)
            p = self.embed_program(p)
        for q in self.primitives:
            i = self.primitives[q]
            if p != None: print(f"predicted {nn_pred[i]:.2f} expected {p[i]} for {q}")
            else: print(f"predicted {nn_pred[i]:.2f} for {q}")

def diff_I_for_NN(grid_gen):
    reds = pickle_read('data_for_nn/diff_I_red_depth3.pickle')
    reds = [reds[0], reds[3], reds[6]]
    pcfgs, _ = pickle_read('ARC_data/diff_I_data_3.pickle')
    while True:
        try:
            p, t1, t2, a = reds[random.randrange(3)]
            p1 = next(pcfgs[t1].sampling())
            while not appears(p1, 0) and a != 1: p1 = next(pcfgs[t1].sampling())
            p2 = next(pcfgs[t2].sampling())
            while not appears(p2, 0) and a != 2: p2 = next(pcfgs[t2].sampling())
            if a == 1: p = Function(Lambda(p), [Lambda(p2)])
            elif a == 2: p = Function(Lambda(p), [Lambda(p1)])
            else: p = Function(Lambda(Lambda(p)), [Lambda(p2), Lambda(p1)])
            try:
                pb, _ = next(grid_gen)
                try_pb_p(dsl, p, pb)
                yield pb, p, None
            except GeneratorExit: return
            except: pass
        except GeneratorExit: return
        
def batch_generator(embed_all_tasks, embed_all_programs, batch_size=64):
    diff_I = diff_I_for_NN(grid_generator_cor())
    while True:
        try:
            tasks, programs = [], []
            for _ in range(batch_size):
                pb, p, _ = next(diff_I)
                tasks.append(pb)
                programs.append(p)
            yield tasks, embed_all_programs(programs)
        except GeneratorExit: return

if __name__ == "__main__":
    # k = 0
    # img = np.zeros((7,7))
    # # img[0,0], img[0,2], img[1,1], img[2,0], img[2,2] = 2, 2, 2, 2, 2
    # # img[1,4], img[1,6], img[2,5], img[3,4], img[3,6] = 2, 2, 2, 2, 2
    # # img[4,0], img[4,2], img[5,1], img[6,0], img[6,2] = 2, 2, 2, 2, 2
    # img[1,0], img[1,1], img[0,2], img[2,2] = 4, 4, 4, 4
    # # img[2,0], img[2,1], img[1,2], img[3,2] = 4, 4, 4, 4
    # # img[5,3], img[5,4], img[4,5], img[6,5] = 4, 4, 4, 4
    # # img[0,4], img[1,4], img[2,4], img[2,5] = 1, 1, 1, 1
    # # img[0], img[2] = img[2], np.copy(img[0])
    # for i in range(3):
    #     img[i], img[6 - i] = img[6 - i], np.copy(img[i])
    # plt.gca().set_axis_off()
    # plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    # plt.margins(0,0)
    # plt.gca().xaxis.set_major_locator(plt.NullLocator())
    # plt.gca().yaxis.set_major_locator(plt.NullLocator())
    # plt.pcolormesh(img, cmap=cmap, norm=norm, edgecolor='xkcd:dark gray', linewidth=.01)
    # plt.savefig("o1emb.png", bbox_inches='tight', pad_inches=0.0)
    # plt.show()
    # input()
    # k = 0
    # for pb, p, _ in diff_I_for_NN(grid_generator_cor()):
    #     if p.function.body.function.primitive != 'filter': continue
    #     pb_to_grid(pb)
    #     display_pb(pb, format(p))
    #     plt.show(block=False)
    #     print(p)
    #     if input() == '0':
    #         plt.close('all')
    #         for mode in pb:
    #             for pair in pb[mode]:
    #                 for io in pair:
    #                     img = pair[io]
    #                     # plt.pcolormesh(img, cmap=cmap, norm=norm, edgecolor='xkcd:dark gray', linewidth=.01)
    #                     # plt.show(block=False)
    #                     plt.gca().set_axis_off()
    #                     plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    #                     plt.margins(0,0)
    #                     plt.gca().xaxis.set_major_locator(plt.NullLocator())
    #                     plt.gca().yaxis.set_major_locator(plt.NullLocator())
    #                     n, m = len(img), len(img[0])
    #                     img_ = np.zeros((max(n, m), max(n, m)))
    #                     for i in range(n):
    #                         for j in range(m): img_[n - i - 1][j] = img[i][j]
    #                     plt.pcolormesh(img_, cmap=cmap, norm=norm, edgecolor='xkcd:dark gray', linewidth=.01)
    #                     # plt.show()
    #                     plt.savefig(f"{k}.png", bbox_inches='tight', pad_inches=0.0)
    #                     k += 1
    #                         # img_ = np.zeros((max(n, m) ** 2, max(n, m) ** 2))
    #                         # for i in range(n):
    #                         #     for j in range(m):
    #                         #         img_[i * m + j][0] = img[n - i - 1][m - j - 1]
    #                         # plt.close('all')
    #                         # plt.gca().set_axis_off()
    #                         # plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    #                         # plt.margins(0,0)
    #                         # plt.gca().xaxis.set_major_locator(plt.NullLocator())
    #                         # plt.gca().yaxis.set_major_locator(plt.NullLocator())
    #                         # plt.pcolormesh(img_, cmap=cmap, norm=norm, edgecolor='xkcd:dark gray', linewidth=.01)
    #                         # # plt.show()
    #                         # plt.savefig(f"{k}.png", bbox_inches='tight', pad_inches=0.0)
    #                         # k += 1
    #                     plt.close('all')
    #     plt.close('all')

    programs = [solutions[name] for name in solutions]
    tasks = []
    for name in solutions:
        pb = json_read('ARC/data/training/'+name)
        c_type = cohesions[name]
        for mode in pb:
            for pair in pb[mode]:
                pair['input'] = find_objects(pair['input'], c_type), 30, 30
                pair['output'] = find_objects(pair['output'], c_type)
        tasks.append(pb)

    name = 'rnn'
    network = 'new'
    mode = 'train'
    lr = 1e-3
    batch_size = 64
    epochs = 50
    if network == 'reopen':
        try: NN = torch.load('data_for_nn/'+name+'.pt')
        except: NN = torch.load('data_for_nn/'+name+'_backup.pt')
    elif network == 'new': NN = Net(DS_primitive_types)
    # em = NN.embed_all_tasks(tasks)
    # print(em.shape)
    # input()
    # for em_i in em:
    #     plt.imshow(em_i)
    #     plt.show(block=False)
    #     if input() == '0': break
    #     plt.close('all')
    batch_gen = batch_generator(NN.embed_all_tasks, NN.embed_all_programs, batch_size)
            
    if mode == 'train':
        x, y, y_aux, i = [], [], [], 0
        plt.ion()
        i = 0
        for loss_value in NN.train(batch_gen, epochs=epochs, lr=lr):
            y.append(loss_value)           
            if i % epochs == 0:
                x.append(i // epochs)
                y_aux.append(np.mean(y))
                print(y_aux[-1])
                plt.plot(x[5:], y_aux[5:])
                plt.pause(0.01)
                plt.draw()
                if i % (20 * epochs) == 0 and i > 0:
                    torch.save(NN, 'data_for_nn/'+name+'.pt')
                    a = input("satisfying?")
                    if a == '1':
                        mode = 'test'
                        break
                elif i % (20 * epochs) == 10 * epochs: torch.save(NN, 'data_for_nn/'+name+'_backup.pt')
            i += 1
            
    if mode == 'test':
        solutions = [solutions[name] for name in solutions]
        # for i in range(len(solutions)):
        #     NN.test(tasks[i], solutions[i])
        #     if input() == '0': break
        for pb, p, _ in diff_I_for_NN(grid_generator_cor()):
            NN.test(pb, p, pb)
            if input() == '0': break
            plt.close('all')