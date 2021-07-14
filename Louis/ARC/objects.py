import numpy as np, copy, matplotlib.pyplot as plt
from matplotlib import colors
cmap = colors.ListedColormap(['#000000', '#0074D9', '#FF4136', '#2ECC40', '#FFDC00', '#AAAAAA', '#F012BE', '#FF851B', '#7FDBFF', '#870C25'])
norm = colors.Normalize(0, 9)

class Object():
    # cohesion_type = 'contact' -> contacts par arêtes uniquement et objet multicolor
    # = 'contact and color' -> idem mais unicolor
    # = 'contact by point' -> contacts par points et multicolor
    # = 'contact by point and color'
    def __init__(self, points = [], low_coord = None, high_coord = None, cohesion_type = 'contact', color = None):
        self.cohesion_type = cohesion_type
        # position du point en haut à gauche et en bas à droite du plus petit rectangle qui contient l'objet
        self.low = low_coord
        self.high = high_coord
        self.points = sorted(points) # coordonnées relatives par rapport à low_coord
        self.color = color
        
    def __repr__(self):
        s = '\nObject: c_type: '+self.cohesion_type+', color: '+format(self.color)+', low: '+format(self.low)+', high: '+format(self.high)+'\nPoints: '
        for p in self.points:
            s += format(p)+" "
        return s

    def same(self, other, mode = 'both'):
        self.points.sort()
        other.points.sort()
        if mode == 'both':
            return self.points == other.points
        elif mode == 'shape':
            for (i, j, _), (i_, j_, _) in zip(self.points, other.points):
                if i != i_ or j != j_:
                    return False
            return True
        elif mode == 'color':
            if self.color == None and other.color == None: return False
            else: return self.color == other.color
    
    def nb_points(self):
        return len(self.points)
    
    def rectangle_size(self): #(height, width) of the smallest rectangle the object fits in
        if self.points == []: return 0, 0
        return self.high[0] - self.low[0] + 1, self.high[1] - self.low[1] + 1
    
    def is_rectangle(self):
        n, m = self.rectangle_size()
        return self.size == n * m

    def display(self, mode='display'):
        if self.color != 0 :
            img = np.zeros(self.rectangle_size())
        else :
            img = np.ones(self.rectangle_size())
        for i, j, c in self.points:
            img[i][j] = c
        if mode == 'display':
            _, ax = plt.subplots(1)
            ax.invert_yaxis()
            ax.pcolormesh(img, cmap=cmap, norm=norm, edgecolor='xkcd:dark gray', linewidth=.01)
            ax.set_title('Location : {}, {}'.format(self.low[0], self.low[1]))
            #plt.show(block = False)
        else:
            return img

    def duplicate(self):
        return copy.deepcopy(self)
    
    def translate(self, i, j, mode = 'absolute'):
        if mode == 'relative':
            self.low = self.low[0] + i, self.low[1] + j
            self.high = self.high[0] + i, self.high[1] + j
        else:
            x, y = self.rectangle_size()
            self.low = i, j
            self.high = i + x - 1, j + y - 1
        return self
    
    def change_color(self, c):
        self.color = c
        self.points = [(i, j, c) for i, j, _ in self.points]
        return self
    
    def symetry_x(self):
        if self.points == []:
            return self
        n = self.high[0] - self.low[0]
        self.points = [(int(2 * (n / 2) - i), j, c) for i, j, c in self.points]
        return self

    def symetry_y(self):
        if self.points == []:
            return self
        n = self.high[1] - self.low[1]
        self.points = [(i, int(2 * (n / 2) - j), c) for i, j, c in self.points]
        return self

    # def rotate(self):
    #     if self.points == []:
    #         return self
    #     x_low, y_low = self.low
    #     x_high, y_high = self.high
    #     self.high = x_low + y_high - y_low, y_low + x_high - x_low
    #     self.points = [(j - y_low + x_low, i - x_low + y_low, c) for i, j, c in self.points]
    #     return self.symetry_y()
    
    def rotate(self):
        if self.points == []:
            return self
        a, b = self.rectangle_size()
        a, b = (a - 1) / 2, (b - 1) / 2
        self.points = [(a + b - j, b - a + i, c) for i, j, c in self.points]
        a, b = 0, 0
        for i, j, _ in self.points:
            if i - int(i) != 0:
                a = 0.5
            if j - int(j) != 0:
                b = 0.5
        self.points = [(int(i + a), int(j + b), c) for i, j, c in self.points]
        a, b = min(self.points, key=lambda x: x[0])[0], min(self.points, key=lambda x: x[1])[1]
        self.points = [(i - a, j - b, c) for i, j, c in self.points]
        self.high = self.low[0] + max(self.points, key=lambda x: x[0])[0], self.low[1] + max(self.points, key=lambda x: x[1])[1]
        return self
    
    def __eq__(self, other):
        return self.low == other.low and self.same(other, 'both') 
        



def find_object_aux(grid, checked, cohesion_type, background_color, n, m, i, j, points):
    if cohesion_type[:7] == 'contact':
        to_check = []
        if j < m-1:
            to_check.append((i, j+1))
            if i < n-1 and cohesion_type[:16] == 'contact by point':
                to_check.append((i+1, j+1))
        if i < n-1:
            to_check.append((i+1, j))
            if j > 0 and cohesion_type[:16] == 'contact by point':
                to_check.append((i+1, j-1))
        if i > 0:
            to_check.append((i-1, j))
            if j < m-1 and cohesion_type[:16] == 'contact by point':
                to_check.append((i-1, j+1))
        if j > 0:
            to_check.append((i, j-1))
            if i > 0 and cohesion_type[:16] == 'contact by point':
                to_check.append((i-1, j-1))

        for x, y in to_check:
            if checked[x, y] == 0 and grid[x][y] != background_color and ((grid[x][y] == grid[i][j] and cohesion_type[-5:] == 'color') or cohesion_type[-5:] != 'color'):
                checked[x, y] = 1
                points.append((x, y, grid[x][y]))
                points = find_object_aux(grid, checked, cohesion_type, background_color, n, m, x, y, points)

    return points

def find_objects_color(grid, background_color):
    objects = []
    for c in range(10):
        if c != background_color:
            points = [(i, j, c) for i in range(len(grid)) for j in range(len(grid[0])) if grid[i][j] == c]
            if points != []:
                obj = Object(points=points, cohesion_type='color', color=c)
                obj.low = min(obj.points, key=lambda x: x[0])[0], min(obj.points, key=lambda x: x[1])[1]
                obj.high = max(obj.points, key=lambda x: x[0])[0], max(obj.points, key=lambda x: x[1])[1]
                obj.points = [(i - obj.low[0], j - obj.low[1], c) for i, j, c in obj.points]
                objects.append(obj)
            
    return objects

def find_objects(grid, cohesion_type = 'contact by point and color', background_color = 0):
    objects = []
    n, m = len(grid), len(grid[0])
    checked = np.zeros((n, m))
    if cohesion_type[:7] == 'contact':
        for i in range(n):
            for j in range(m):
                if checked[i, j] == 0 and grid[i][j] != background_color:
                    checked[i, j] = 1
                    points = find_object_aux(grid, checked, cohesion_type, background_color, n, m, i, j, [(i, j, grid[i][j])])
                    if cohesion_type[-5:] == 'color':
                        color = grid[i][j]
                    else:
                        color = None
                    obj = Object(points=points, cohesion_type=cohesion_type, color=color)
                    obj.low = min(obj.points, key=lambda x: x[0])[0], min(obj.points, key=lambda x: x[1])[1]
                    obj.high = max(obj.points, key=lambda x: x[0])[0], max(obj.points, key=lambda x: x[1])[1]
                    obj.points = [(i - obj.low[0], j - obj.low[1], c) for i, j, c in obj.points]
                    objects.append(obj)
    if cohesion_type == 'color':
        objects = find_objects_color(grid, background_color)
    
    return objects

def objects_to_grid(objects, n = None, m = None, supple=False, background_color = 0):
    objects = [obj for obj in objects if obj]
    if objects == []: return [[]]
    if n == None:
        n = min(max(objects, key=lambda obj: obj.high[0]).high[0] + 1, 30)
    if m == None:
        m = min(max(objects, key=lambda obj: obj.high[1]).high[1] + 1, 30)
    if supple:
        n = min(max(n, max(objects, key=lambda obj: obj.high[0]).high[0] + 1), 30)
        m = min(max(m, max(objects, key=lambda obj: obj.high[1]).high[1] + 1), 30)
    if n <= 0 or m <= 0: return [[]]
    grid = np.ones((n, m)) * background_color
    for obj in objects:
        for i, j, c in obj.points:
            if 0 <= i + obj.low[0] < n and 0 <= j + obj.low[1] < m and 0 <= c <= 9:
                grid[i + obj.low[0]][j + obj.low[1]] = c
    return grid

# def add_pixel(obj, i, j, c):
#     obj.points.append((i, j, c))
#     obj.update()
#     return obj

# def delete_pixel(obj, i, j):
#     obj.points = [(x, y, c) for x, y, c in obj.points if x != i or y != j]
#     obj.update()
#     return obj

def display(img):
    _, ax = plt.subplots(1)
    ax.invert_yaxis()
    ax.pcolormesh(img, cmap=cmap, norm=norm, edgecolor='xkcd:dark gray', linewidth=.01)
    plt.show(block=False)
    
def fill(i, j, n, m, c):
    if n < 0 or m < 0:
        return None
    points = [(i + x, j + y, c) for x in range(n+1) for y in range(m+1)]
    return Object(points=points, low_coord = (i, j), high_coord = (i + n, j + m), cohesion_type='contact and color', color=c)

def display_pb(pb, title=''):
    train = pb['train']
    test = pb['test']
    n = len(train)
    fig, plots = plt.subplots(n, 5)
    fig.suptitle(title)
    for i in range(n):
        plots[i][0].invert_yaxis()
        plots[i][0].pcolormesh(train[i]['input'], cmap=cmap, norm=norm, edgecolor='xkcd:dark gray', linewidth=.01)
        plots[i][0].set_title('Example {} : input'.format(i+1))
        plots[i][1].invert_yaxis()
        plots[i][1].pcolormesh(train[i]['output'], cmap=cmap, norm=norm, edgecolor='xkcd:dark gray', linewidth=.01)
        plots[i][1].set_title('output')
        for j in range(5):
            plots[i][j].axis('off')
    n = len(test)
    for i in range(n):
        plots[i][3].invert_yaxis()
        plots[i][3].pcolormesh(test[i]['input'], cmap=cmap, norm=norm, edgecolor='xkcd:dark gray', linewidth=.01)
        plots[i][3].set_title('Test {} : input'.format(i+1))
        plots[i][4].invert_yaxis()
        plots[i][4].pcolormesh(test[i]['output'], cmap=cmap, norm=norm, edgecolor='xkcd:dark gray', linewidth=.01)
        plots[i][4].set_title('solution')
    # plt.show()

# grid = np.array([[0,0,0],[1,1,1],[0,1,0],[0,0,0]])
# obj = find_objects(grid)[0]
# obj.display()
# obj.rotate().display()
# print(obj.same(n_obj))
# obj.display()
# obj.rotate()
# print(obj)
# obj.display()

# plt.show()