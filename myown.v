module myown(
in1,
in2,
in3,
clk,
out1,
out2,
out3
);



input in1;
input in2;
input in3;
input clk;

output out1;
output out2;
output out3;

wire _1_; 
wire _2_;
wire _3_;


XOR2_X1 xor1 ( .a(in1), .b(in2), .o(_1_) ); done
fflopd ff ( .CK(clk), .D(_1_), .Q(_3_) );  done
INV_X2 inv1 ( .a(in3), .o(_2_) ); done
INV_X2 inv2 ( .a(_2_), .o(out2) ); done
INV_X2 inv3 ( .a(_1_), .o(out3) ); done
XOR2_X1 xor2 ( .a(_3_), .b(_2_), .o(out1) );