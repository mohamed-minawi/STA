from scipy.interpolate import interp2d
import numpy as np

class output_pin:
    def __init__(self, name, data ):
        self.name = name
        self.data = data
        self.rise_capacitance = 0.0
        self.fall_capacitance = 0.0
        self.capacitance = 0.0
        self.timing_dic = {}

        self.index1 = []
        self.index2 = []


        self.__parse()
    
    def __parse(self):
        timing_index = []
        timing = []
        flag = True

        for index, line in enumerate(self.data):
            if "rise_capacitance" in line:
                self.rise_capacitance = float(line.split()[2].replace(";",""))
            elif "fall_capacitance" in line:
                self.fall_capacitance = float(line.split()[2].replace(";",""))
            elif "capacitance" in line:
                self.capacitance = float(line.split()[2].replace(";",""))
            elif "timing()" in line:
                timing_index.append(index)
            elif "internal_power" in line:
                timing_index.append(index)
                flag = False
                break;

        if flag:
            timing_index.append(len(self.data)-1)

        for index in range(len(timing_index)-1):
            timing.append(self.data[timing_index[index]:timing_index[index + 1]])

        pin_name = []
        timing_sense = []
        cell_rise = []
        cell_fall = []
        rise_transition = []
        fall_transition = []

        ind = None
        boolflag = [0,0,0,0]
        for tim in timing:
            for index, line in enumerate(tim):
                if "timing_sense" in line:
                    timing_sense.append(line.split()[2])
                elif "related_pin" in line:
                    pin_name.append(line.split()[2])
                elif "cell_rise" in line:
                    boolflag[0] = 1
                    ind = index
                elif "rise_transition" in line:
                    boolflag[1] = 1
                    ind = index
                elif "cell_fall" in line:
                    boolflag[2] = 1
                    ind = index
                elif "fall_transition" in line:
                    boolflag[3] = 1
                    ind = index
                elif "}" in line:
                    if boolflag[0]:
                        cell_rise.append(tim[ind:index+1])
                        boolflag[0] = 0
                    elif boolflag[1]:
                        rise_transition.append(tim[ind:index+1])
                        boolflag[1] = 0
                    elif boolflag[2]:
                        cell_fall.append(tim[ind:index+1])
                        boolflag[2] = 0
                    elif boolflag[3]:
                        fall_transition.append(tim[ind:index+1])
                        boolflag[3] = 0
        for i in range(len(pin_name)):
            self.timing_dic[pin_name[i]] = [timing_sense[i], cell_rise[i],cell_fall[i],rise_transition[i],fall_transition[i]]
    def returnTiming(self):
        return self.timing_dic

class input_pin:
    def __init__(self, name, data ):
        self.name = name
        self.data = data
        self.rise_capacitance = 0.0
        self.fall_capacitance = 0.0
        self.capacitance = 0.0
        self.timing = []

        self.timing_sense = None
        self.index1 = []
        self.index2 = []
        self.cell_rise = []
        self.cell_fall = []
        self.rise_transition = []
        self.fall_transition = []

        self.interp_Cell_Rise = None
        self.interp_cell_fall = None
        self.interp_fall_transition = None
        self.interp_rise_transition = None

        self.__parse()

    def __parse(self):
        for x in self.data:
            if "rise_capacitance" in x:
                self.rise_capacitance = float(x.split()[2].replace(";",""))
            elif "fall_capacitance" in x:
                self.fall_capacitance = float(x.split()[2].replace(";",""))
            elif "capacitance" in x:
                self.capacitance = float(x.split()[2].replace(";",""))

    def addTiming(self,timinglist):
        self.timing = timinglist
        self.__parsetiming()

        self.index1 = np.array(self.index1)
        self.index2 = np.array(self.index2)
        self.cell_fall = np.array(self.cell_fall)
        self.cell_rise = np.array(self.cell_rise)
        self.rise_transition = np.array(self.rise_transition)
        self.fall_transition = np.array(self.fall_transition)
        
        self.interp_Cell_Rise = interp2d(self.index2, self.index1, self.cell_rise)
        self.interp_cell_fall = interp2d(self.index2, self.index1, self.cell_fall)
        self.interp_fall_transition = interp2d(self.index2, self.index1, self.fall_transition)
        self.interp_rise_transition = interp2d(self.index2, self.index1, self.rise_transition)

    def __parsetiming(self):
        
        boolflag = [0,0,0,0]
        valflag = [0,0,0,0]
        for i in range(len(self.timing)):
            if i == 0:
                self.timing_sense = self.timing[i]
            else:
                for x in self.timing[i]:
                    if "cell_rise" in x:
                        boolflag = [1,0,0,0]
                    elif "cell_fall" in x:
                        boolflag = [0,1,0,0]                    
                    elif "rise_transition" in x:
                        boolflag = [0,0,1,0]                    
                    elif "fall_transition" in x:
                        boolflag = [0,0,0,1]                    
                    y = x.split()

                    if boolflag[0]:
                        if "index_1" in x:
                            for i in y:
                                if "(" in i:
                                    self.index1.append(float(i.replace("(","").replace('"',"").replace(",","")))
                                elif "," in i:
                                    self.index1.append(float(i.replace(",","")))     
                                elif ")" in i:
                                    self.index1.append(float(i.replace(")","").replace('"',"").replace(",","").replace(";","")))
                        elif "index_2" in x:
                            for i in y:
                                nk = 0
                                if "(" in i:
                                    self.index2.append(float(i.replace("(","").replace('"',"").replace(",","")))
                                elif "," in i:
                                    self.index2.append(float(i.replace(",","")))     
                                elif ")" in i:
                                    self.index2.append(float(i.replace(")","").replace('"',"").replace(",","").replace(";","")))
                        else:
                            if "value" in x or valflag[0]:
                                valflag = [1,0,0,0]
                                arr = []
                                for i in y:
                                    if '"' in i:
                                        arr.append(float(i.replace('"',"").replace(",","").replace(")","").replace(";","").replace("/","").replace("(","")))
                                    elif ',' in i:
                                        arr.append(float(i.replace(",","")))
                                self.cell_rise.append(arr[:])
                                arr = []
                    elif boolflag[1]:
                            if "value" in x or valflag[1]:
                                valflag = [0,1,0,0]
                                arr = []
                                for i in y:
                                    if '"' in i:
                                        arr.append(float(i.replace('"',"").replace(",","").replace(")","").replace(";","").replace("/","").replace("(","")))
                                    elif ',' in i:
                                        arr.append(float(i.replace(",","")))
                                self.cell_fall.append(arr[:])
                                arr = []
                    elif boolflag[2]:
                            if "value" in x or valflag[2]:
                                valflag = [0,0,1,0]
                                arr = []
                                for i in y:
                                    if '"' in i:
                                        arr.append(float(i.replace('"',"").replace(",","").replace(")","").replace(";","").replace("/","").replace("(","")))
                                    elif ',' in i:
                                        arr.append(float(i.replace(",","")))
                                self.rise_transition.append(arr[:])
                                arr = []
                    elif boolflag[3]:
                            if "value" in x or valflag[3]:
                                valflag = [0,0,0,1]
                                arr = []
                                for i in y:
                                    if '"' in i:
                                        arr.append(float(i.replace('"',"").replace(",","").replace(")","").replace(";","").replace("/","").replace("(","")))
                                    elif ',' in i:
                                        arr.append(float(i.replace(",","")))
                                self.fall_transition.append(arr[:])
                                arr = []


        self.cell_rise = list(filter(None, self.cell_rise))
        self.cell_fall = list(filter(None, self.cell_fall))
        self.fall_transition = list(filter(None, self.fall_transition))
        self.rise_transition = list(filter(None, self.rise_transition))

    def calculateGateDelay(self, cload, inputslew):
        one = self.interp_cell_fall(inputslew, cload)
        two = self.interp_Cell_Rise(inputslew, cload)

        return (max(one,two))

    def calculateGateOutSlew(self, cload, inputslew):
        one = self.interp_fall_transition(inputslew, cload)
        two = self.interp_rise_transition(inputslew, cload)

        return (max(one,two))

class Cell:
    def __init__(self, name,data):
        self.pin_dict = { }
        self.name = name
        self.data = data

        self.__parse()
    def __parse(self):
        pins_index = []
        pins = []
        pin = []

        for p in self.data:
            for index, line in enumerate(p):
                if 'pin(' in line or "pin (" in line:
                    pins_index.append(index)
            pins_index.append(len(p))
            for index in range(len(pins_index)-1):
                pin.append(p[pins_index[index]:pins_index[index+1]])
            pins.append(p[:])
            pin.clear()
            pins_index.clear()
        timing_dic = {}
        out = None
        for pin in pins:
            name = pin[0]
            name = name.replace("pin(","").replace("pin (","").replace(")","").replace("{","").replace('"',"").replace(" ","")

            direction, directionout = pin[1].split()[2].replace(";",""),  pin[1].split()[2].replace(";","")
            directioninp = pin[2].split()[2].replace(";","")
            if directioninp == "input" or direction == "input":
                self.pin_dict[name] = input_pin(name, pin)
            else:
                self.pin_dict[name] = output_pin(name, pin)
                out = name
        
        timing_dic = self.pin_dict[out].returnTiming()
        keys = list(timing_dic.keys())
        value = list(timing_dic.values())

        names = list(self.pin_dict.keys())
        for i in range(len(keys)):
            t = keys[i].replace('"', "").replace(";","")
            self.pin_dict[t].addTiming(value[i])

    def returnPinCapacitance(self, pin_name):
        temp = self.pin_dict[pin_name]
        return temp.capacitance

    def returnPinDelay(self, pin, cload, inpslew):
        temp = self.pin_dict[pin]
        return temp.calculateGateDelay(cload, inpslew) 

    def returnPinOutSlew(self, pin, cload, inpslew):
        temp = self.pin_dict[pin]
        return temp.calculateGateOutSlew(cload, inpslew) 

class Liberty_Parser:
    def __init__(self, path):
        self.path = path
        self.cells_dict = {}

        self.__parse()
    def __readfileforparsing(self,name):
        with open(name) as f:
            filelines = f.readlines()
        return [x[:x.find("#")].strip() if "#" in x else x.strip() for x in filelines]
    def __parse(self):
        array = self.__readfileforparsing(self.path)
        cells_index = []
        cells = []
        cell_names = []
        for index, line in enumerate(array):
            if ('cell (' in line):
                line = line.split()
                cell_names.append(line[1].replace("(","").replace(")","").replace('"',""))
                cells_index.append(index)
        cells_index.append(len(array))      
        for index  in range(len(cells_index)-1):
            cells.append(array[cells_index[index]:cells_index[index + 1]])

        pins_index = []
        pins = []
        pin = []
        for cell in cells:
            for index, line in enumerate(cell):
                if 'pin(' in line or "pin (" in line:
                    pins_index.append(index)
            pins_index.append(len(cell))
            for index in range(len(pins_index)-1):
                pin.append(cell[pins_index[index]:pins_index[index+1]])
            pins.append(pin[:])
            pin.clear()
            pins_index.clear()

        for x in range(len(cell_names)):
            self.cells_dict[cell_names[x].replace("(","").replace(")","")] = Cell(cell_names[x],pins[x])

    def returncell_capacitance(self, name, pin):
        temp = self.cells_dict[name]
        return temp.returnPinCapacitance(pin)

    def returnDelay(self, name, pin, cload, inpslew): 
        temp = self.cells_dict[name]
        return temp.returnPinDelay(pin, cload, inpslew)

    def returnSlew(self, name, pin, cload, inpslew): 
        temp = self.cells_dict[name]
        return temp.returnPinOutSlew(pin, cload, inpslew)
    


