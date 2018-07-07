set PERIOD 196

reset_design
create_clock -period $PERIOD -name clk [get_ports clk]
set_clock_uncertainty 0.05 [get_clocks clk]
set_ideal_network [get_ports clk]

set ALL_INS_EX_CLK [remove_from_collection [all_inputs] [get_ports clk]]


set_input_delay -clock clk 10 A
set_input_delay -clock clk 15 B
set_input_delay -clock clk 20 C
set_input_delay -clock clk 8 D
set_output_delay -clock clk 3.5 X
set_output_delay -clock clk 4.9 Y
set_input_transition -clock clk 15 A
set_input_transition -clock clk 10 B
set_input_transition -clock clk 40 C
set_input_transition -clock clk 21 D

set_driving_cell -lib_cell IBUFFX4_RVT  -pin Y $ALL_INS_EX_CLK

set max_cap [expr [load_of saed32rvt_ff1p16v125c/AND2X1_RVT/A1] * 10]
set_max_capacitance $max_cap $ALL_INS_EX_CLK

set_load [expr 3 * $max_cap] [all_outputs]

set_max_area 0