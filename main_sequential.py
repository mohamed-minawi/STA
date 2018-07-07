from SDC_Parser import *
from SPEF_Parser import *
from Liberty_Parser import *
from Verilog_Parser import *
import math

if __name__ == "__main__":

    name = input("Please input name of the file (without extensions): ") 
        

    inputs, outputs, wires ,filecells = parse(name+'.v')	
    DAG = createDAG(inputs, outputs, wires ,filecells)
    paths = DAG.traverse()

    print("All Possible Paths: \n")
    for x in paths:
        print("Path: ", x)
        print("\n---------------------------------------------------------------\n")

    input("")