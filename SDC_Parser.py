class SDC_Parser:
    def __init__(self, name):
        self.values = {}
        self.__constraintvals(name)

    def __readfileforparsing(self,name):
        with open(name) as f:
            filelines = f.readlines()
        return filelines

    def __constraintvals(self,filename):
        
        filecontent = self.__readfileforparsing(filename)
        period = load = maxcap = ""
        input, output, transition = [], [], []
        for i in filecontent:
            if('set PERIOD' in i):
                period = i.replace("set PERIOD ", "")
            if('set_input_delay' in i):
                input.append(i)
            if('set_output_delay' in i):
                output.append(i)
            if('set_load' in i):
                load = i
            if('set max_cap' in i):
                maxcap = i
            if('set_input_transition' in i):
                transition.append(i)

        arrload = load.split()
        arrmaxcap = maxcap.split()
        
        fmaxcap = arrmaxcap[4].replace("]", "")
        
        loadfactor = arrload[2]        
        c = 0
        a = 0 
        b = 0

        self.values["Input Delay"], self.values["Output Delay"], self.values["Input Transition"]  = [], [], []
        arrout, arrin, arrtransition  = [], [], []   

        while(c<input.__len__()):
            arrin.append(input[c].split())
            if('$ALL_INS_EX_CLK' in input[c]):
                inputdelay = arrin[c][2].replace("$PERIOD*", "").replace("]", "").replace(" ", "")
                self.values["Input Delay for all"] = [inputdelay]
            elif(" *" in input[c]):
                self.values["Input Delay for all"] = [float(arrin[c][3])]
            else:
                self.values["Input Delay"].append([arrin[c][4], float(arrin[c][3])])
            c = c + 1

        while(a<output.__len__()):
            arrout.append(output[a].split())
            if('all_outputs' in output[a]):
                outputdelay = arrout[a][2].replace("$PERIOD*", "").replace("]", "").replace(" ", "")
                self.values["Output Delay for all"] = [outputdelay]
            elif(" *" in output[a]):
                self.values["Output Delay for all"] = [float(arrout[a][3])]
            else:
                self.values["Output Delay"].append([arrout[a][4], float(arrout[a][3])])
            a = a + 1


        while( b < transition.__len__()):
            arrtransition.append(transition[b].split())
            if(" *" in transition[b]):
                self.values["Input Transition for all"] = [float(arrtransition[b][3])]
            else:
                self.values["Input Transition"].append([arrtransition[b][4], float(arrtransition[b][3])])
            b = b + 1 


        self.values["Period"] = [float(period)]

        self.values["Load Factor"] = [float(loadfactor)]
        self.values["Max Cap of gate name : "] = [fmaxcap]