import torch, logging, os, sys, random
sys.path.insert(0, '..')
from torch import nn

from Louis.solutions import *
from Louis.misc import *
from Louis.grids import grid_generator_cor
from Louis.ARC_generator import appears, dsl

class Net(nn.Module):
    def __init__(self, nb_inputs_max=6):
        super(Net, self).__init__()
        self.nb_inputs_max = nb_inputs_max
        self.net = nn.Sequential(
            nn.Linear(12600, 4096),
            nn.ReLU(),
            nn.Linear(4096, 2048),
            nn.ReLU(),
            nn.Linear(2048, 1024),
            nn.ReLU(),
            nn.Linear(1024, 900),
        )
        self.loss = torch.nn.MSELoss()

    def forward(self, embedded_tasks): return self.net(embedded_tasks)

    def embed_list_obj(self, list_objects):
        grid = torch.zeros(30, 30)
        for obj in list_objects:
            for i, j, c in obj.points:
                if 0 <= i + obj.low[0] < 30 and 0 <= j + obj.low[1] < 30 and 0 <= c <= 9:
                    grid[i + obj.low[0], j + obj.low[1]] = c
        return grid

    def embed_task(self, pb):
        res = []
        for i in range(self.nb_inputs_max):  # if more inputs there are ignored
            try:
                pair = pb['train'][i]
                em_input = self.embed_list_obj(pair['input'][0])
                em_output = self.embed_list_obj(pair['output'])
                res.append(torch.cat([em_input, em_output], dim=1))
            except:
                res.append(torch.zeros(30, 60))
        test = self.embed_list_obj(pb['test'][0]['input'][0])
        test = torch.cat([test, torch.zeros(30, 30)], dim=1)
        res.append(test)
        return torch.reshape(torch.cat(res), (-1,)) # (14, 30, 60)

    def embed_all_tasks(self, tasks):
        res = []
        for task in tasks: res.append(self.embed_task(task))
        return torch.stack(res) # (batch_size, 14, 30, 60)
    
    def embed_res(self, pb):
        return torch.reshape(self.embed_list_obj(pb['test'][0]['output']), (-1,))
    
    def embed_all_res(self, pbs):
        return torch.stack([self.embed_res(pb) for pb in pbs])
    
    def train(self, batch_generator, epochs=200, lr=1e-4):
        optimizer = torch.optim.Adam(self.parameters(), lr=lr)
        for embedded_tasks, embedded_res in batch_generator:
            for _ in range(epochs):
                optimizer.zero_grad()
                nn_preds = self(embedded_tasks)
                loss_value = self.loss(nn_preds, embedded_res)
                loss_value.backward()
                optimizer.step()
                yield loss_value.item()

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
        
def batch_generator(embed_all_tasks, embed_all_res):
    diff_I = diff_I_for_NN(grid_generator_cor())
    while True:
        try:
            tasks = []
            for _ in range(64):
                pb, _, _ = next(diff_I)
                tasks.append(pb)
            yield embed_all_tasks(tasks), embed_all_res(tasks)
        except GeneratorExit: return

if __name__ == "__main__":
    # for pb, p, _ in diff_I_for_NN(grid_generator_cor()):
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

    name = 'trash'
    network = 'new'
    mode = 'test'
    lr = 1e-4
    if network == 'reopen':
        try: NN = torch.load('data_for_nn/'+name+'.pt')
        except: NN = torch.load('data_for_nn/'+name+'_backup.pt')
    elif network == 'new': NN = Net()
    # em = NN.embed_task(tasks[4])
    # print(em.shape)
    
    if mode == 'test':
        try: NN = torch.load('data_for_nn/'+name+'.pt')
        except: NN = torch.load('data_for_nn/'+name+'_backup.pt')
        solutions = [solutions[name] for name in solutions]
        for i in range(len(solutions)):
            plt.imshow((torch.reshape(NN(NN.embed_all_tasks([tasks[i]])).detach(), (30, 30))))
            pb_to_grid(tasks[i])
            display_pb(tasks[i])
            plt.show(block=False)
            if input() == '0': break
            plt.close('all')
        for pb, p, _ in diff_I_for_NN(grid_generator_cor()):
            NN.test(pb, p)
            if input() == '0': break
            
    elif mode == 'train':
        x, y, y_aux, i = [], [], [], 0
        plt.ion()
        batch_gen = batch_generator(NN.embed_all_tasks, NN.embed_all_res)
        i = 0
        for loss_value in NN.train(batch_gen, epochs=20, lr=lr):
            y.append(loss_value)           
            if i % 20 == 0:
                x.append(i // 20)
                y_aux.append(np.mean(y))
                print(y_aux[-1])
                plt.plot(x, y_aux)
                plt.pause(0.01)
                plt.draw()
                if i % 40 == 0: torch.save(NN, 'data_for_nn/'+name+'.pt')
                else: torch.save(NN, 'data_for_nn/'+name+'_backup.pt')
            i += 1