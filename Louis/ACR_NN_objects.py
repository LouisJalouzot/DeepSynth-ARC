import torch, logging, os, sys, random
sys.path.insert(0, '..')
from torch import nn

from Louis.solutions import *
from Louis.misc import *
from Louis.grids import grid_generator_cor
from Louis.ARC_generator import appears, dsl

class Color_embedder(nn.Module):
    def __init__(self):
        super(Color_embedder, self).__init__()
        self.net = nn.Linear(10, 1)
        
    def forward(self, c):
        color = torch.zeros(10)
        color[c] = 1
        return self.net(color)
    
class X_coord_embedder(nn.Module):
    def __init__(self):
        super(X_coord_embedder, self).__init__()
        self.net = nn.Linear(30, 1)
        
    def forward(self, i):
        x = torch.zeros(30)
        x[i] = 1
        return self.net(x)
    
class Y_coord_embedder(nn.Module):
    def __init__(self):
        super(Y_coord_embedder, self).__init__()
        self.net = nn.Linear(30, 1)
        
    def forward(self, j):
        y = torch.zeros(30)
        y[j] = 1
        return self.net(y)
    
class Combiner(nn.Module):
    def __init__(self):
        super(Combiner, self).__init__()
        self.net = nn.Linear(3, 1)
        
    def forward(self, c, i, j):
        res = torch.Tensor([c, i, j])
        return self.net(res)
    
class Obj_fe(nn.Module):
    def __init__(self, size_obj_max, obj_feature_extractor_dim):
        super(Obj_fe, self).__init__()
        self.size_obj_max = size_obj_max
        self.obj_feature_extractor_dim = obj_feature_extractor_dim
        self.net = nn.Sequential(
            nn.Linear(self.size_obj_max, self.size_obj_max),
            nn.Linear(self.size_obj_max, self.obj_feature_extractor_dim),
            nn.Linear(self.obj_feature_extractor_dim, self.obj_feature_extractor_dim)
        )
        
    def forward(self, obj):
        return self.net(obj)
    
class IO_fe(nn.Module):
    def __init__(self, io_input_dim, io_feature_extractor_dim):
        super(IO_fe, self).__init__()
        self.io_input_dim = io_input_dim
        self.io_feature_extractor_dim = io_feature_extractor_dim
        self.net = nn.Sequential(
            nn.Linear(self.io_input_dim, self.io_input_dim),
            nn.Linear(self.io_input_dim, self.io_feature_extractor_dim),
            nn.Linear(self.io_feature_extractor_dim, self.io_feature_extractor_dim),
        )
        
    def forward(self, input, output):
        return self.net(torch.cat([input, output]))

class Net(nn.Module):
    def __init__(self, primitive_types, nb_inputs_max=6, nb_obj_max=10, size_obj_max=86, obj_feature_extractor_dim=50, io_feature_extractor_dim=300):
        super(Net, self).__init__()
        self.nb_inputs_max = nb_inputs_max
        self.primitives = {p: i for i, p in enumerate(primitive_types.keys())}
        self.nb_primitives = len(self.primitives)
        self.size_obj_max = size_obj_max
        self.obj_feature_extractor_dim = obj_feature_extractor_dim
        self.nb_obj_max = nb_obj_max
        self.io_feature_extractor_dim = io_feature_extractor_dim
        self.color_embedder = Color_embedder()
        self.x_coord_embedder = X_coord_embedder()
        self.y_coord_embedder = Y_coord_embedder()
        self.combiner = Combiner()
        self.embedded_pixel = torch.zeros(10, 30, 30)
        self.obj_feature_extractor = Obj_fe(self.size_obj_max, self.obj_feature_extractor_dim)
        self.io_input_dim = self.obj_feature_extractor_dim * self.nb_obj_max * 2
        self.io_feature_extractor = IO_fe(self.io_input_dim, self.io_feature_extractor_dim)
        self.net = nn.Sequential(
            nn.Linear(self.io_feature_extractor_dim * self.nb_inputs_max, 1024),
            nn.Linear(1024, 512),
            nn.Linear(512, 256),
            nn.Linear(256, self.nb_primitives),
        )
        self.loss = torch.nn.MSELoss()
    
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
    
    def forward_obj(self, obj):
        embedded_obj = torch.zeros(self.size_obj_max)
        for index, (i, j, c) in enumerate(obj.points):
            embedded_obj[index] = self.embedded_pixel[c, i, j]
        return self.obj_feature_extractor(embedded_obj)
    
    def forward_list_obj(self, list_obj):
        res = torch.zeros(self.nb_obj_max, self.obj_feature_extractor_dim)
        for index, obj in enumerate(list_obj):
            if index >= self.nb_obj_max: break
            res[index] = self.forward_obj(obj)
        return torch.reshape(res, (-1,))
    
    def forward_io(self, pair):
        input = self.forward_list_obj(pair['input'][0])
        output = self.forward_list_obj(pair['output'])
        return self.io_feature_extractor(input, output)
    
    def forward_task(self, task):
        embedded_task = torch.zeros(self.nb_inputs_max, self.io_feature_extractor_dim)
        for index, pair in enumerate(task['train']):
            embedded_task[index] = self.forward_io(pair)
        return torch.reshape(embedded_task, (-1,))
    
    def forward(self, tasks):
        forwarded_tasks = []
        embedded_color = torch.zeros(10)
        for c in range(10):
            embedded_color[c] = self.color_embedder(c)
        embedded_xcoords, embedded_ycoords = torch.zeros(30), torch.zeros(30)
        for x in range(30):
            embedded_xcoords[x] = self.x_coord_embedder(x)
            embedded_ycoords[x] = self.y_coord_embedder(x)
        for c in range(10):
            for i in range(30):
                for j in range(30): self.embedded_pixel[c, i, j] = self.combiner(embedded_color[c], embedded_xcoords[i], embedded_ycoords[j])
        for task in tasks:
            embedded_task = self.forward_task(task)
            forwarded_task = self.net(embedded_task)
            forwarded_tasks.append(forwarded_task)
        return torch.stack(forwarded_tasks)
    
    def train(self, batch_generator, epochs=200, lr=1e-4):
        optimizer = torch.optim.Adam(self.parameters(), lr=lr)
        for tasks, embedded_programs in batch_generator:
            for _ in range(epochs):
                optimizer.zero_grad()
                loss_value = self.loss(self(tasks), embedded_programs)
                loss_value.backward()
                optimizer.step()
                yield loss_value.item()
                    
    def test(self, task, p=None):
        nn_pred = self(self.embed_all_tasks([task]))[0]
        if p != None :
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
        
def batch_generator(embed_all_programs):
    diff_I = diff_I_for_NN(grid_generator_cor())
    while True:
        try:
            tasks, programs = [], []
            for _ in range(64):
                pb, p, _ = next(diff_I)
                tasks.append(pb)
                programs.append(p)
            yield tasks, embed_all_programs(programs)
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

    name = 'objects'
    network = 'new'
    mode = 'train'
    lr = 1e-3
    if network == 'reopen':
        try: NN = torch.load('data_for_nn/'+name+'.pt')
        except: NN = torch.load('data_for_nn/'+name+'_backup.pt')
    elif network == 'new': NN = Net(DS_primitive_types)
    # em = NN.forward_obj(tasks[4]['train'][0]['input'][0][0])
    # plt.imshow(torch.stack([em.detach()]))
    # plt.show()
    # em = NN.forward_list_obj(tasks[4]['train'][0]['input'][0])
    # plt.imshow(torch.stack([em.detach()]))
    # plt.show()
    # em = NN.forward_io(tasks[4]['train'][0])
    # plt.imshow(torch.stack([em.detach()]))
    # plt.show()
    # em = NN.forward_task(tasks[4])
    # plt.imshow(torch.stack([em.detach()]))
    # plt.show()
    # em = NN.forward(tasks)
    # input()
    if mode == 'test':
        try: NN = torch.load('data_for_nn/'+name+'.pt')
        except: NN = torch.load('data_for_nn/'+name+'_backup.pt')
        solutions = [solutions[name] for name in solutions]
        # for i in range(len(solutions)):
        #     NN.test(tasks[i], solutions[i])
        #     if input() == '0': break
        for pb, p, _ in diff_I_for_NN(grid_generator_cor()):
            NN.test(pb, p)
            if input() == '0': break
            
    elif mode == 'train':
        x, y, y_aux, i = [], [], [], 0
        plt.ion()
        batch_gen = batch_generator(NN.embed_all_programs)
        i = 0
        for value in NN.train(batch_gen, epochs=20, lr=lr):
            y.append(value)           
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