class Embedding():
    '''
    Embeds a list of pairs of grids
    '''

    def __init__(self, ) -> None:
        pass

    def embed_grid(self, list_objects):
        number_objects = len(list_objects)
        grid = torch.zeros(30 * 30 * (1 + number_objects))
        for index, obj in enumerate(objects):
            for i, j, c in obj.points:
                if 0 <= i + obj.low[0] < n and 0 <= j + obj.low[1] < m and 0 <= c <= 9:
                    grid[i + obj.low[0] + 30 * (j + obj.low[1])] = c
                    grid[i + obj.low[0] + 30 * (j + obj.low[1]) + 30 * 30 * index] = 1
        return grid

    def embed_IO(self, args):
        '''
        embed a list of inputs and its associated output
        args = list containing the inputs and the associated output in the format args ::= [[i1,i2,...],o], where any i1, i2, .. and o are lists of floats
        '''
        res = []
        inputs, output = args
        for i in range(self.nb_inputs_max):  # if more inputs there are ignored
            try:
                input = inputs[i]
                embedded_input = self.embed_grid(input)
                res.append(embedded_input)
            except:
                res.append(torch.zeros(2*self.size_max))

        res.append(self.embed_single_arg(output))
        return torch.cat(res)

    def embed_all_examples(self, IOs):
        '''
        Embed a list of IOs (it simply stacks the embedding of a single input/output pair)
        '''
        res = []
        for IO in IOs:
            res.append(self.embed_IO(IO))
        return torch.stack(res)
