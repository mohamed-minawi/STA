class DNET:
    def __init__(self, inputs, output, name, graph, cap, res):
        self.name = name
        self.input = inputs
        self.output = output
        self.graph = graph
        self.cap = cap
        self.res = res
        self.possiblePaths = []

        self.pathRC = []

        self.find_Possible_path()

        self.find_RCPaths()
        
    def returnPathCapacitance(self, drivenGate, cload):
        index = None
        for i in range(len(self.possiblePaths)):
            if drivenGate in self.possiblePaths[i][-1]:
                index = i
                break;
        if index is None:
            return

        path = self.pathRC[index]
        path.append("C"+str(cload))
        cap = 0
        for x in path:
            if "C" in x:
                cap += float(x.replace("C",""))

        return cap

    def CalculateWireDelay(self, cload, drivenGate):
        index = None
        for i in range(len(self.possiblePaths)):
            if drivenGate in self.possiblePaths[i][-1]:
                index = i
                break;
        if index is None:
            return
        
        path = self.pathRC[index]
        path.append("C"+str(cload))

        delay = 0
        res = 0

        for i in range(len(path)):
            res, cap = 0 , 0
            if "C" in path[i]:
                cap = float(path[i].replace("C",""))
                for j in range(i+1,len(path)):
                    if "C" in path[j]:
                        cap += float(path[j].replace("C",""))
            elif "R" in path[i]:
                res = float(path[i].replace("R",""))
                for j in range(i+1,len(path)):
                    if "C" in path[j]:
                        cap += float(path[j].replace("C",""))
            delay += res*cap

        return delay
        
    def find_RCPaths(self):
        temp = []
        for x in self.possiblePaths:
            for i in range(len(x)-1):
                temp.append("C"+str(self.cap[x[i]]))
                res = self.__findRes(x[i], x[i+1])
                temp.append("R"+ str(res))
            temp.append("C"+str(self.cap[x[-1]]))
            self.pathRC.append(temp[:])
            temp = []

    def __findRes(self, n1, n2):
        for i in range(len(self.res)):
            if self.res[i][0] == n1 and self.res[i][1] == n2:
                return self.res[i][2]

    def find_Possible_path(self):
        for x in self.input:
            temp = self.__find_path(self.graph, self.output, x)
            self.possiblePaths.append(temp)

    def __find_path(self, graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if start not in graph:
            return None
        for node in graph[start]:
            if node not in path:
                newpath = self.__find_path(graph, node, end, path)
                if newpath: 
                    return newpath
        return None
     
class SPEF_Parser:
    def __init__(self, path):
        self.path = path
        self.dnet_dict = {}

        self.__parse()

    def __readfileforparsing(self,name):
        with open(name) as f:
            filelines = f.readlines()
        return [x[:x.find("#")].strip() if "#" in x else x.strip() for x in filelines]

    def __parse(self):
        array = self.__readfileforparsing(self.path)
        dnet_index = []
        dnets = []
        dnet_names = []
        for index, line in enumerate(array):
            if ('D_NET ' in line):
                line = line.split()
                dnet_names.append(line[1])
                dnet_index.append(index)
        dnet_index.append(len(array))      
        for index  in range(len(dnet_index)-1):
            dnets.append(array[dnet_index[index]:dnet_index[index + 1]])

        for x in dnets:
            name, d = self.__parseDnet(x)
            self.dnet_dict[name] = d
    
    def __parseDnet(self, data):
        input = []
        out = ""
        name = ""
        capactitances = {}
        resistances = []
        graph = {}
        boolflag = [False, False, False]
        for x in data:
            if "D_NET" in x:
                name = x.split()[1]
            elif "CONN" in x:
                boolflag =[True, False, False]
            elif "CAP" in x:
                boolflag =[False, True, False]
            elif "RES" in x:                
                boolflag =[False, False, True]
            temp = x.split()
            if boolflag[0]:
                if len(temp) > 1:
                    if temp[2] == "O":
                        out = temp[1]
                    else:
                        input.append(temp[1])
            elif boolflag[1]:
                if len(temp) > 1:
                    graph[temp[1]] = []
                    capactitances[temp[1]] = float(temp[2])
            elif boolflag[2]:
                if len(temp) > 1:
                    graph[temp[1]].append(temp[2])
                    resistances.append([temp[1], temp[2], float(temp[3])])

        return name, DNET(input, out, name, graph, capactitances, resistances)
                
    def returnWireCapacitance(self, DnetName, drivingGate,cload):
        temp = self.dnet_dict[DnetName]
        return temp.returnPathCapacitance(drivingGate, cload)
    
    def CalculateWireDelay(self, DnetName ,drivingGate, cload):
        temp = self.dnet_dict[DnetName]
        return temp.CalculateWireDelay(cload, drivingGate)