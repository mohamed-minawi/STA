from SDC_Parser import *
from SPEF_Parser import *
from Liberty_Parser import *
from Verilog_Parser import *
import math

def assignDelays(toporder, DAG, sdc, spef, lib):
    for x in toporder:
        if DAG.vert_dict[x].direction == "Input":
            delay, slew = findSDC(sdc, x)
            DAG.vert_dict[x].delay = delay
            DAG.vert_dict[x].inp_slew = slew
        elif DAG.vert_dict[x].direction == "Gate":
           
            inpslew = math.inf *-1
            tempslew = None
            for pre in DAG.vert_dict[x].prev.keys():
                wire = DAG.vert_dict[x]
                if pre.direction == "Wire":
                    wire = pre
                    pre = list(pre.prev.keys())[0]
                    for n in pre.out_slw:
                        if n[0] == x:
                            tempslew = n[1]
                elif pre.direction == "Input":
                    tempslew = pre.inp_slew

                inpslew = max(inpslew,tempslew)
            outcap = []
            cap = None
            for succ in DAG.vert_dict[x].adjacent.keys():
                if succ.direction == "Wire":
                    for succwire in succ.adjacent.keys():
                        pinload = lib.returncell_capacitance(succwire.gate_type, succwire.pin)
                        cap = spef.returnWireCapacitance(succ.id, succwire.id, pinload)
                        outcap.append([succwire.id, cap])
                elif succ.direction == "Output":
                    pinload = lib.returncell_capacitance(succwire.gate_type, "o")
                    outcap.append([succwire.id, pinload])
                        
            for z in outcap:
                name= z[0]
                outslew = lib.returnSlew(DAG.vert_dict[x].gate_type,DAG.vert_dict[x].pin, z[1], inpslew)
                DAG.vert_dict[x].out_slw.append([name, outslew])

            DAG.vert_dict[x].delay = lib.returnDelay(DAG.vert_dict[x].gate_type,DAG.vert_dict[x].pin, z[1], inpslew)
        elif DAG.vert_dict[x].direction == "Wire":
            pred = list(DAG.vert_dict[x].prev.keys())[0];
            s = []
            succarr = []
            for succ in DAG.vert_dict[x].adjacent.keys():
                s.append(succ)
                succarr.append([succ.id, succ.gate_type,succ.pin])
            succ_cap = []
            for z in succarr:
                succ_cap.append(lib.returncell_capacitance(z[1],z[-1]))

            for i in range(len(s)):
                wiredelay = spef.CalculateWireDelay(x, succarr[i][0], succ_cap[i])
                DAG.vert_dict[x].adjacent[s[i]] = wiredelay;
   
def findSDC(sdc, name):
    delay, slew = None, None;
    for x in sdc.values["Input Delay"]:
        if x[0] == name:
            delay = x[1]
            break;
    for x in sdc.values["Input Transition"]:
        if x[0] == name:
            slew = x[1]
            break;
    return delay, slew

def GenerateTimingReport(paths, DAG):
    for path in paths:
        print("Path: ", path, "\n")
        for node in path:
            if DAG.vert_dict[node].direction != "Wire":
                print("Node: ", node, DAG.vert_dict[node].slack)
        print("\n--------------------------------------------------------------------\n")


if __name__ == "__main__":

    name = input("Please input name of the file (without extensions): ") 
        
    sdc = SDC_Parser(name + ".sdc")
    spef = SPEF_Parser(name + ".spef")
    lib = Liberty_Parser(name + ".lib")

    inputs, outputs, wires ,filecells = parse(name+'.v')	
    DAG = createDAG(inputs, outputs, wires ,filecells)
    paths = DAG.traverse()
    topOrder, topOrder2 = DAG.topologicalSort()

    assignDelays(topOrder, DAG, sdc, spef, lib)

    DAG.AAT(topOrder2)
    DAG.RAT(topOrder2, sdc.values["Period"][0])
    DAG.calculateSlack()

    CP, slack = indentifyCP(paths, DAG)
    print("\nCriical Path: ",CP, "Slack: ",slack, "\n\n")

    print("Timing Reports:\n\n--------------------------------------------------------------------")
    GenerateTimingReport(paths, DAG)

    input("")