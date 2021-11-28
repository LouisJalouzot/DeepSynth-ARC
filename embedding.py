import torch 
import torch.nn as nn

class ResidualBlock(nn.Module):
    
    def __init__(self, blocks=None):
        super(ResidualBlock, self).__init__()

        self.layers = nn.ModuleList(blocks)

    def forward(self, x):
        ipt = x.clone().to(x.device)
        for layer in self.layers:
            x = layer(x)
            x.add_(ipt)
            x = torch.functional.relu(x)
        return x

class Embedding(nn.Module):
    '''
    Embeds a list of pairs of grids
    '''
    def __init__(self, max_objects=10):
        super(Embedding, self).__init__()
        self.max_objects = max_objects
        self.size_max = self.max_objects * 30 * 30
        self.nb_inputs_max = 6
        # self.net = nn.Sequential(
        #     ResidualBlock([
        #         nn.Conv2d(self.max_objects, self.max_objects, 3, padding='same'),
        #         nn.Conv2d(self.max_objects, self.max_objects, 3, padding='same'),
        #         nn.Conv2d(self.max_objects, self.max_objects, 3, padding='same'),
        #     ]),
        #     nn.Conv2d(self.max_objects, 2 * self.max_objects, 5),
        #     nn.Conv2d(2 * self.max_objects, 3 * self.max_objects, 5),
        #     nn.MaxPool2d(3),
        #     nn.Flatten()
        # )
        total_input_channels = self.max_objects * 2 * self.nb_inputs_max
        self.net = nn.Sequential(
            nn.Conv2d(total_input_channels,
                      total_input_channels // 2, 3), # Divide channels by 2 and decreases grid size to 28x28 and channels=60
            nn.ReLU(),
            nn.Conv2d(total_input_channels // 2,
                      total_input_channels // 4, 3),  # Divide channels by 2 and decreases grid size to 26x26 and channels=30
            nn.MaxPool2d(3), # Max Pool takes a kernel of size 3 and map it to the max of that kernel, grid size is now 24x24 and channels=30
            nn.ReLU(),       # At this stage we are down to 17 280 parameters
            nn.Conv2d(total_input_channels // 4,
                      total_input_channels // 4, 3),#, padding = 'same'), # grid size is 22x22
            nn.ReLU(),
            nn.Flatten()
        )
        self.output_dimensionality = 1080

    def embed_grid(self, list_objects):
        n, m = 30, 30
        grid = torch.zeros(self.max_objects, 30, 30)
        for index, obj in enumerate(list_objects):
            if index >= self.max_objects: break
            for i, j, c in obj.points:
                if 0 <= i + obj.low[0] < n and 0 <= j + obj.low[1] < m and 0 <= c <= 9:
                    grid[0, i + obj.low[0], j + obj.low[1]] = c
                    grid[index, i + obj.low[0], j + obj.low[1]] = 1
        return grid

    def embed_IO(self, args):
        '''
        embed a list of inputs and its associated output
        args = list containing the inputs and the associated output in the format args ::= [[i1,i2,...],o], where any i1, i2, .. and o are lists of floats
        '''
        res = []
        for i in range(self.nb_inputs_max):  # if more inputs there are ignored
            try:
                input, output = args[i]
                em_input = self.embed_grid(input)
                em_output = self.embed_grid(output)
                res.append(em_input)
                res.append(em_output)
            except:
                res.append(torch.zeros(self.max_objects, 30, 30))
                res.append(torch.zeros(self.max_objects, 30, 30))
        return torch.cat(res)

    def embed_all_examples(self, IOs):
        '''
        Embed a list of IOs (it simply stacks the embedding of a single input/output pair)
        '''
        res = []
        for IO in IOs:
            res.append(self.embed_IO(IO))
        return self.net(torch.reshape(torch.stack(res), (-1, self.nb_inputs_max * 2 * self.max_objects, 30, 30)))
    
    def forward(self, tasks):
        return self.embed_all_examples(tasks)
    
if __name__ == "__main__":
    Embedding()