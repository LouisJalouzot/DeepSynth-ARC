import torch, logging, os, sys, random, time
sys.path.insert(0, '..')
from torch import nn

from Louis.solutions import *
from Louis.misc import *
from Louis.grids import grid_generator_cor
from Louis.ARC_generator import appears, dsl

class Embedding(nn.Module):
    def __init__(self, primitive_types, third=10, nb_inputs_max=6):
        super(Embedding, self).__init__()
        self.third = third
        self.nb_inputs_max = nb_inputs_max
        self.primitives = {p: i for i, p in enumerate(primitive_types.keys())}
        self.nb_primitives = len(self.primitives)
        self.nb_channels = self.nb_inputs_max * 2
        self.color_net = nn.Linear(self.third, 1)
        self.object_net = nn.Linear(self.third, 1)
        self.combine_net = nn.Linear(2, 1)
        self.net = nn.Sequential( # (batch_size, 12, 30, 30)
            nn.Flatten() # (batch_size, 10800)
        )
        self.output_dim = 10800
        
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
        grid = torch.zeros(30, 30)
        for index, obj in enumerate(list_objects):
            if index >= self.third: break
            for i, j, c in obj.points:
                if 0 <= i + obj.low[0] < 30 and 0 <= j + obj.low[1] < 30 and 0 <= c <= 9:
                    obj_v = torch.zeros(self.third)
                    obj_v[index] = 1
                    embedded_obj = self.object_net(obj_v)
                    color_v = torch.zeros(self.third)
                    color_v[c] = 1
                    embedded_color = self.color_net(color_v)
                    grid[i + obj.low[0], j + obj.low[1]] = self.combine_net(torch.Tensor([embedded_obj, embedded_color]))
        return grid

    def embed_task(self, pb):
        res = []
        for i in range(self.nb_inputs_max):  # if more inputs there are ignored
            try:
                pair = pb['train'][i]
                em_input = self.embed_list_obj(pair['input'][0])
                em_output = self.embed_list_obj(pair['output'])
                res.append(em_input)
                res.append(em_output)
            except:
                res.append(torch.zeros(30, 30))
                res.append(torch.zeros(30, 30))
        return torch.stack(res)
    
    def embed_all_tasks(self, tasks):
        res = []
        for task in tasks: res.append(self.embed_task(task))
        return torch.stack(res) # (batch_size, nb_channels, 30, 30)
    
    def forward(self, embedded_tasks): return self.net(embedded_tasks)

class Net(nn.Module):
    def __init__(self, embedder):
        super(Net, self).__init__()
        self.embedder = embedder
        self.net = nn.Sequential(
            nn.Linear(embedder.output_dim, 4096),
            nn.ReLU(),
            nn.Linear(4096, 1024),
            nn.ReLU(),
            nn.Linear(1024, self.embedder.nb_primitives),
        )
        self.loss = torch.nn.MSELoss()

    def forward(self, embedded_tasks): return self.net(embedded_tasks)
    
    def train(self, batch_generator, epochs=200, lr=1e-4):
        optimizer = torch.optim.Adam(self.parameters(), lr=lr)
        for embedded_tasks, embedded_programs in batch_generator:
            for step in range(epochs):
                optimizer.zero_grad()
                # start = time.time()
                nn_preds = self.embedder(embedded_tasks)
                # if step == 0: print('embedder net', time.time() - start)
                # start = time.time()
                nn_preds = self(nn_preds)
                # if step == 0: print('main net', time.time() - start)
                # start = time.time()
                loss_value = self.loss(nn_preds, embedded_programs)
                loss_value.backward(retain_graph=True)
                optimizer.step()
                # if step == 0: print('backward + step', time.time() - start)
                yield loss_value.item()
                    
    def test(self, task, p=None): 
        nn_pred = self(self.embedder(self.embedder.embed_all_tasks([task])))[0]
        if p != None :
            print(p)
            p = self.embedder.embed_program(p)
        for q in self.embedder.primitives:
            i = self.embedder.primitives[q]
            if p != None:
                print(f"predicted {nn_pred[i].item():.2f} expected {p[i]} for {q}")
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
        
def batch_generator(embed_all_tasks, embed_all_programs):
    diff_I = diff_I_for_NN(grid_generator_cor())
    while True:
        try:
            tasks, programs = [], []
            # start = time.time()
            for _ in range(64):
                pb, p, _ = next(diff_I)
                tasks.append(pb)
                programs.append(p)
            # print('gen', time.time() - start)
            # start = time.time()
            embedded_tasks = embed_all_tasks(tasks)
            # print('embed tasks', time.time() - start)
            # start = time.time()
            embedded_programs = embed_all_programs(programs)
            # print('embed programs', time.time() - start)
            yield embedded_tasks, embedded_programs
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


    ############################## SETTINGS
    name = 'cunning'
    network = 'new'
    mode = 'train'
    lr = 1e-3
    if network == 'reopen':
        try: NN = torch.load('data_for_nn/'+name+'.pt')
        except: NN = torch.load('data_for_nn/'+name+'_backup.pt')
    elif network == 'new':
        E = Embedding(DS_primitive_types_to_learn)
        NN = Net(E)
    # em = NN.embedder.embed_all_tasks(tasks)
    # print(em.shape)
    # plt.imshow(torch.cat([torch.cat([em[4, 2 * i], em[4, 2 * i + 1]], dim=1) for i in range(6)]).detach())
    # plt.show()
    # em = NN(NN.embedder(em))
    # print(em.shape)
    
    if mode == 'test':
        try: NN = torch.load('data_for_nn/'+name+'.pt')
        except: NN = torch.load('data_for_nn/'+name+'_backup.pt')
        solutions = [solutions[name] for name in solutions]
        for i in range(len(solutions)):
            NN.test(tasks[i], solutions[i])
            if input() == '0': break
        for pb, p, _ in diff_I_for_NN(grid_generator_cor()):
            NN.test(pb, p)
            if input() == '0': break
            
    elif mode == 'train':
        x, y, y_aux, i = [], [], [], 0
        plt.ion()
        batch_gen = batch_generator(NN.embedder.embed_all_tasks, NN.embedder.embed_all_programs)
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