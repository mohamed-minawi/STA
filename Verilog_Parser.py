import math

class Vertex:
    def __init__(self, gate_iname, type = "", gate_type =  "",pin = "",delay = 0):
        self.id = gate_iname
        self.pin = pin
        self.direction = type
        self.gate_type = gate_type
        self.delay = delay
        self.adjacent = {}
        self.prev = {}
        self.RAT = None
        self.AAT = None
        self.slack = None
        self.inp_slew = None
        self.out_slw = []

    def __str__(self):
        return str(self.id) + ' adjacent: ' + str([x for x in self.adjacent.keys()]) + " prev " + str([x.id for x in self.prev])  + " Slack " + str(self.slack) 

    def add_neighbor(self, neighbor, weight=0):
        self.adjacent[neighbor] = weight

    def get_connections(self):
        return self.adjacent.keys()  

    def get_id(self):
        return self.id

    def get_type(self):
        return self.direction

    def get_weightN(self, neighbor):
        return self.adjacent[neighbor]

    def get_weightP(self, neighbor):
        return self.prev[neighbor]
class Graph:
    def __init__(self):
        self.vert_dict = {}
        self.num_vertices = 0

    def __iter__(self):
        return iter(self.vert_dict.values())

    def add_vertex(self, gate_iname, type = "", gate_type =  "",pin = "",delay = 0):
        if gate_iname not in self.vert_dict:
            self.num_vertices = self.num_vertices + 1
            new_vertex = Vertex(gate_iname, type, gate_type, pin)
            self.vert_dict[gate_iname] = new_vertex
        else:
            if self.vert_dict[gate_iname].direction == "Wire":
                self.vert_dict[gate_iname].direction = type

    def get_vertex(self, n):
        if n in self.vert_dict:
            return self.vert_dict[n]
        else:
            return None

    def add_edge(self, frm, to, cost = 0):
        if frm not in self.vert_dict:
            self.add_vertex(frm)
        if to not in self.vert_dict:
            self.add_vertex(to)

        self.vert_dict[frm].add_neighbor(self.vert_dict[to], cost)
        self.vert_dict[to].prev[self.vert_dict[frm]] = cost

    def get_vertices(self):
        return self.vert_dict.keys()
    
    def find_path(self, start, end, path=[]):
        path = path + [start.id]
        if start.id in end:
            return [path]
        if start.id not in self.vert_dict.keys():
            return []
        paths = []
        for node in self.vert_dict[start.id].adjacent.keys():
            if node.id not in path:
                newpaths = self.find_path(node, end, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths

    def traverse(self):
        verticies = self.vert_dict.values()
        input = [arr for arr in verticies if arr.direction == "Input"]
        output = [arr.id for arr in verticies if arr.direction == "Output"]
        p = []
        for inp in input:
            for out in output:
                paths = self.find_path(inp,out)
                for path in paths:
                    p.append(path)
        return p

    def topologicalSort(self):
        in_degree = {}
        for x in self.vert_dict.keys():
            in_degree[x] = 0;

        for x in self.vert_dict.values():
            for y in x.adjacent.keys():
                in_degree[y.id] +=1

        queue = []
        for x in in_degree.keys():
            if in_degree[x] == 0:
                queue.append(x)

        cnt = 0
        toporder = []

        while queue:
            u = queue.pop(0)
            toporder.append(u)

            for x in self.vert_dict[u].adjacent.keys():
                in_degree[x.id] -= 1
                if in_degree[x.id] == 0:
                    queue.append(x.id)
            cnt += 1
        arr = []
        toporder2 = toporder[:]
        for x in toporder:
            if self.vert_dict[x].direction == "Wire":
                arr.append(x)
        for z in arr:
            toporder2.remove(z)
        return toporder, toporder2
    
    def AAT(self, topOrder):
        self.vert_dict["Root"].AAT = 0
        wire = None
        temp = None
        for x in topOrder:
            if x != "Root":
                self.vert_dict[x].AAT = self.vert_dict[x].delay
                temp = math.inf * -1
                for pre in self.vert_dict[x].prev.keys():
                    wire = self.vert_dict[x]
                    if pre.direction == "Wire":
                        wire = pre
                        pre = list(pre.prev.keys())[0]

                    temp = max(temp,self.vert_dict[x].AAT + pre.AAT + pre.get_weightN(wire))
                self.vert_dict[x].AAT = temp

    def RAT(self, topOrder, period):
        topOrder.reverse()
        for x in self.vert_dict.values():
            if x.direction == "Output":
                x.RAT = period
        wire = None
        temp = None
        for x in topOrder:
            if self.vert_dict[x].direction != "Output":
                temp =  math.inf
                for succ in self.vert_dict[x].adjacent.keys():
                    wire = self.vert_dict[x]
                    if succ.direction == "Wire":
                        wire = succ
                        succ = list(succ.adjacent.keys())[0]
                        temp = min(temp, succ.RAT - succ.delay - succ.get_weightP(wire))
                    elif succ.direction == "Output":
                        temp = succ.RAT - succ.get_weightP(wire)
                    elif succ.direction == "Gate":
                        temp = min(temp, succ.RAT - succ.delay - succ.get_weightP(wire))
                        
                        

                self.vert_dict[x].RAT = temp
    
    def calculateSlack(self):
        for x in self.vert_dict.values():
            if x.direction != "Wire" and x.direction != "Root":
                x.slack = x.RAT - x.AAT

def readfileforparsing(name):
   with open(name) as f:
       filelines = f.readlines()
   return [x[:x.find("//")].strip() if "//" in x else x.strip() for x in filelines ] 

def parse(name):
    vcontent = readfileforparsing(name)
    inputs = []
    outputs =[]
    wires = []
    filecells = []

    temparr = []

    for arr in vcontent:
        if "input" in arr:
            inputs.append(arr.replace("input",'').replace(";","").replace(" ",""))
        elif "output" in arr:
            outputs.append(arr.replace("output",'').replace(";","").replace(" ",""))
        elif "wire" in arr:
            wires.append(arr.replace("wire",'').replace(";","").replace(" ",""))
        elif len(arr.split()) >= 6:
            temp = arr.split()
            for i in range(len(temp)):
                if i == 0 or i == 1:
                    temparr.append(temp[i])
                elif i != 2 and i != len(temp)-1:
                    temparr.append(temp[i].replace(",","").replace(".",""))
            filecells.append(temparr[:])
        temparr = []
                     
    return inputs, outputs, wires ,filecells

def createDAG(inputs, outputs, wires ,gates):
    def split_expr(expr):
        loc = expr.find("(")
        return expr[:loc], expr[loc+1:].replace(")","")

    outputpins = ["Y", "YS", "YC", "DI","YPAD", "Q","Z","ZN", "QN", "CO", "S", "o"]

    DAG = Graph()
    DAG.add_vertex("Root", "Root")

    for arr in inputs:
        DAG.add_vertex(arr, "Input")
        DAG.add_edge("Root", arr)

    for arr in outputs:
        DAG.add_vertex(arr, "Output")

    for arr in wires:
        DAG.add_vertex(arr, "Wire")


    
    dff = False
    afterout = ""
    inp = []
    for arr in gates:
        for x in range(2,len(arr)):
            gate_type = arr[0]
            gate_iname = arr[1]

            before, after = split_expr(arr[x])

            DAG.add_vertex(gate_iname, "Gate", gate_type, before)

            if "DFF" in gate_type or "flop" in gate_type:
                dff = True

            if dff:
                if "D" in before:
                    DAG.add_vertex(after, "Output")
                elif "Q" in before:
                    DAG.add_vertex(after, "Input")
                else:
                    DAG.add_edge(after, gate_iname)
                dff = False         
            else:
                if before in outputpins:
                    DAG.add_edge(gate_iname,after)
                else:
                    DAG.add_edge(after, gate_iname)
    return DAG

def indentifyCP(paths, DAG):
    flg = False
    prev , current = None, None
    cp = None
    for path in paths:
        cp = path
        flg = False
        prev , current = None, None
        for node in path:
            if DAG.vert_dict[node].direction != "Wire" and DAG.vert_dict[node].direction != "Root"  and DAG.vert_dict[node].direction != "Wire" :
                current = DAG.vert_dict[node].slack
                if prev != None:
                    if round(prev[0],5) != round(current[0],5):
                        flg = True
                prev = current
        
        if flg == False:
            return cp, current; 
    return None
