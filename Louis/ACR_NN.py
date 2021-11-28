import torch, logging, os, sys, random
sys.path.insert(0, '..')
from torch import nn

from Louis.solutions import *
from Louis.misc import *
from Louis.grids import grid_generator, grid_generator_cor
from Louis.ARC_generator import appears, dsl

logging_levels = {0: logging.INFO, 1: logging.DEBUG}

class Embedding(nn.Module):
    def __init__(self, primitive_types, max_objects=10, nb_inputs_max=6):
        super(Embedding, self).__init__()
        self.max_objects = max_objects
        self.size_max = self.max_objects * 30 * 30
        self.nb_inputs_max = nb_inputs_max
        self.total_input_channels = self.max_objects * 2 * self.nb_inputs_max
        # self.net = nn.Sequential(
        #     nn.Conv2d(self.total_input_channels, self.total_input_channels // 2, 3), # Divide channels by 2 and decreases grid size to 28x28 and channels=60
        #     nn.ReLU(),
        #     nn.Conv2d(self.total_input_channels // 2, self.total_input_channels // 4, 3),  # Divide channels by 2 and decreases grid size to 26x26 and channels=30
        #     nn.MaxPool2d(3), # Max Pool takes a kernel of size 3 and map it to the max of that kernel, grid size is now 24x24 and channels=30
        #     nn.ReLU(),       # At this stage we are down to 17 280 parameters
        #     nn.Conv2d(self.total_input_channels // 4, self.total_input_channels // 4, 3),#, padding = 'same'), # grid size is 22x22
        #     nn.ReLU(),
        #     nn.Flatten()
        # )
        self.net = nn.Sequential(
            nn.Conv2d(self.total_input_channels, self.total_input_channels // 2, 3),
            nn.ReLU(),
            nn.Conv2d(self.total_input_channels // 2, self.total_input_channels // 2, 3),
            nn.ReLU(),
            nn.Flatten()
        )
        self.output_dim = 40560
        self.primitives = list(primitive_types.keys())
        self.nb_primitives = len(self.primitives)
        
    def embed_program_rec(self, tensor, p):
        if isinstance(p, BasicPrimitive):
            try: tensor[self.primitives.index(p.primitive)] = 1
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
        n, m = 30, 30
        grid = torch.zeros(self.max_objects, 30, 30)
        for index, obj in enumerate(list_objects):
            if index + 1 >= self.max_objects: break
            for i, j, c in obj.points:
                if 0 <= i + obj.low[0] < n and 0 <= j + obj.low[1] < m and 0 <= c <= 9:
                    grid[0, i + obj.low[0], j + obj.low[1]] = c
                    grid[index + 1, i + obj.low[0], j + obj.low[1]] = 1
        return grid

    def embed_task(self, pb, use_test=False):
        if use_test: pb = pb['train']+pb['test']
        else: pb = pb['train']
        res = []
        for i in range(self.nb_inputs_max):  # if more inputs there are ignored
            try:
                pair = pb[i]
                em_input = self.embed_list_obj(pair['input'][0])
                em_output = self.embed_list_obj(pair['output'])
                res.append(em_input)
                res.append(em_output)
            except:
                res.append(torch.zeros(self.max_objects, 30, 30))
                res.append(torch.zeros(self.max_objects, 30, 30))
        return torch.cat(res)

    def embed_all_tasks(self, tasks):
        res = []
        for task in tasks: res.append(self.embed_task(task))
        return torch.reshape(torch.stack(res), (-1, self.total_input_channels, 30, 30))
    
    def forward(self, embedded_tasks): return self.net(embedded_tasks)

class Net(nn.Module):
    def __init__(self, embedder, output_dim):
        super(Net, self).__init__()
        self.embedder = embedder
        self.input_dim = embedder.output_dim
        self.output_dim = output_dim
        self.net = nn.Sequential(
            nn.Linear(self.input_dim, 1024),
            nn.Linear(1024, 256),
            nn.Linear(256, self.output_dim),
        )
        # self.net = nn.Sequential(
        #     nn.Linear(self.input_dim, self.output_dim),
        # )
        self.loss = torch.nn.MSELoss()

    def forward(self, embedded_tasks): return self.net(embedded_tasks)
    
    def train(self, batch_generator, epochs=200, lr=1e-6):
        optimizer = torch.optim.Adam(self.parameters(), lr=lr)
        for embedded_tasks, embedded_programs in batch_generator:
            for step in range(epochs):
                optimizer.zero_grad()
                nn_preds = self(self.embedder(embedded_tasks)) # forward of the 2 networks
                loss_value = self.loss(nn_preds, embedded_programs)
                loss_value.backward()
                optimizer.step()
                yield loss_value.item()

                if step % 50 == 0: logging.debug(f"optimization step {step} loss_value {loss_value.item():.5f}")
                if step % 200 == 0:
                    logging.debug("\n################################ Comparison :")
                    for i in range(self.embedder.nb_primitives):
                        logging.debug(f"predicted {nn_preds[0][i]:.2f} expected {embedded_programs[0][i]} for {self.embedder.primitives[i]}")
                    
    def evaluation_batch(self, embedded_tasks, embedded_programs):
        nn_preds = self(self.embedder(embedded_tasks))
        return self.loss(nn_preds, embedded_programs).item()

    def evaluation(self, pbs, batch_size=64):
        errs = []
        while pbs != []:
            if len(pbs) < batch_size: break
            tasks, programs = [], []
            for _ in range(batch_size):
                pb, p, _ = pbs.pop()
                tasks.append(pb)
                programs.append(p)
            embedded_tasks = self.embedder.embed_all_tasks(tasks)
            embedded_programs = self.embedder.embed_all_programs(programs)
            errs.append(self.evaluation_batch(embedded_tasks, embedded_programs))
        return np.mean(errs)
                    
    def test(self, task, p=None): 
        nn_pred = self(self.embedder(self.embedder.embed_all_tasks([task])))[0]
        if p != None : print(p)
        for i in range(self.embedder.nb_primitives):
            print(f"predicted {nn_pred[i]:.2f} for {self.embedder.primitives[i]}")

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
    grid_gen, grid_gen_cor = grid_generator(), grid_generator_cor()
    diff_I, diff_I_cor = diff_I_for_NN(grid_gen), diff_I_for_NN(grid_gen_cor)
    while True:
        try:
            tasks, programs = [], []
            for _ in range(64):
                pb, p, _ = next(diff_I)
                tasks.append(pb)
                programs.append(p)
                pb, p, _ = next(diff_I_cor)
                tasks.append(pb)
                programs.append(p)
            yield embed_all_tasks(tasks), embed_all_programs(programs)
        except GeneratorExit: return

if __name__ == "__main__":
    verbosity = 0
    logging.basicConfig(format='%(message)s', level=logging_levels[verbosity])
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

    name = 'NN'
    E = Embedding(DS_primitive_types)
    NN = Net(E, E.nb_primitives)
    em = NN.embedder.embed_task(tasks[4])
    plt.imshow(em[12])
    plt.show()
    # print('output_dim: =', E(E.embed_all_tasks(tasks[:1])).shape[1])
    # try: NN = torch.load('data_for_nn/'+name+'.pt')
    # except: NN = torch.load('data_for_nn/'+name+'_backup.pt')
    
    mode = 'test'
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
        for loss_value in NN.train(batch_gen, epochs=20, lr=1e-5):
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