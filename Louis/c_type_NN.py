import torch, logging, os, sys, random
sys.path.insert(0, '..')
from torch import nn

from Louis.solutions import *
from Louis.misc import *
from Louis.grids import grid_generator_cor
from Louis.ARC_generator import appears, dsl

class Net(nn.Module):
    def __init__(self, nb_c_types=5, nb_inputs_max=6):
        super(Net, self).__init__()
        self.nb_inputs_max = nb_inputs_max
        self.nb_c_types = nb_c_types
        self.net = nn.Sequential( # (12, 30, 30)
            nn.Conv2d(self.nb_inputs_max * 2, self.nb_inputs_max * 2, 3), # (12, 28, 28)
            nn.ReLU(),
            nn.Conv2d(self.nb_inputs_max * 2, self.nb_inputs_max, 3), # (12, 26, 26)
            nn.MaxPool2d(2), # (6, 13, 13)
            nn.ReLU(),
            nn.Flatten(), # 
            nn.Linear(1014, 256),
            nn.Linear(256, 64),
            nn.Linear(64, self.nb_c_types),
            nn.Softmax()
        )
        self.loss = torch.nn.MSELoss()

    def forward(self, embedded_tasks): return self.net(embedded_tasks)
    
    def embed_c_type(self, c_type):
        res = torch.zeros(self.nb_c_types)
        res[c_type - 1] = 1
        return res
    
    def embed_all_c_types(self, c_types):
        return  torch.stack([self.embed_c_type(c_type) for c_type in c_types])

    def embed_list_obj(self, list_objects):
        grid = torch.zeros(30, 30)
        for obj in list_objects:
            for i, j, c in obj.points:
                if 0 <= i + obj.low[0] < 30 and 0 <= j + obj.low[1] < 30 and 0 <= c <= 9:
                    grid[i + obj.low[0], j + obj.low[1]] = c
        return grid

    def embed_task(self, pb):
        res = torch.zeros(self.nb_inputs_max * 2, 30, 30)
        for index, pair in enumerate(pb['train']):
            if index >= self.nb_inputs_max: break
            res[2 * index] = self.embed_list_obj(pair['input'][0])
            res[2 * index + 1] = self.embed_list_obj(pair['output'])
        return res

    def embed_all_tasks(self, tasks):
        return torch.stack([self.embed_task(task) for task in tasks])
    
    def train(self, batch_generator, epochs=200, lr=1e-4):
        optimizer = torch.optim.Adam(self.parameters(), lr=lr)
        for embedded_tasks, embedded_programs in batch_generator:
            for _ in range(epochs):
                optimizer.zero_grad()
                nn_preds = self(embedded_tasks)
                loss_value = self.loss(nn_preds, embedded_programs)
                loss_value.backward()
                optimizer.step()
                yield loss_value.item()
                    
    def test(self, task, c_type=None):
        nn_pred = self(self.embed_all_tasks([task]))[0].detach()
        if c_type != None : print(c_type)
        print(f"predicted {nn_pred}")

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
                pb, c_type = next(grid_gen)
                try_pb_p(dsl, p, pb)
                yield pb, p, c_type
            except GeneratorExit: return
            except: pass
        except GeneratorExit: return
        
def batch_generator(embed_all_tasks, embed_all_c_types):
    diff_I = diff_I_for_NN(grid_generator_cor())
    while True:
        try:
            tasks, c_types = [], []
            for _ in range(512):
                pb, _, c_type = next(diff_I)
                tasks.append(pb)
                c_types.append(c_type)
            yield embed_all_tasks(tasks), embed_all_c_types(c_types)
        except GeneratorExit: return

if __name__ == "__main__":
    # for pb, p, c_type in diff_I_for_NN(grid_generator_cor()):
    #     print(c_type)
    #     pb_to_grid(pb)
    #     display_pb(pb, format(p))
    #     plt.show(block=False)
    #     if input() == '0': break
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

    name = 'c_type'
    network = 'new'
    mode = 'train'
    lr = 1e-3
    if network == 'reopen':
        try: NN = torch.load('data_for_nn/'+name+'.pt')
        except: NN = torch.load('data_for_nn/'+name+'_backup.pt')
    elif network == 'new': NN = Net()
    # em = NN.embed_task(tasks[4])
    # for em_i in em:
    #     plt.imshow(em_i)
    #     plt.show(block=False)
    #     if input() == '0': break
    #     plt.close('all')
    
    if mode == 'test':
        solutions = [solutions[name] for name in solutions]
        # for i in range(len(solutions)):
        #     NN.test(tasks[i], solutions[i])
        #     if input() == '0': break
        for pb, _, c_type in diff_I_for_NN(grid_generator_cor()):
            NN.test(pb, c_type)
            if input() == '0': break
            
    elif mode == 'train':
        x, y, y_aux, i = [], [], [], 0
        plt.ion()
        batch_gen = batch_generator(NN.embed_all_tasks, NN.embed_all_c_types)
        i = 0
        for loss_value in NN.train(batch_gen, epochs=200, lr=lr):
            y.append(loss_value)           
            if i % 20 == 0:
                x.append(i // 20)
                y_aux.append(np.mean(y))
                print(y_aux[-1])
                plt.plot(x[5:], y_aux[5:])
                plt.pause(0.01)
                plt.draw()
                if i % 40 == 0: torch.save(NN, 'data_for_nn/'+name+'.pt')
                else: torch.save(NN, 'data_for_nn/'+name+'_backup.pt')
            i += 1