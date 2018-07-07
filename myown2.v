module myown2(
A,
B,
C,
D,
X,
Y
);



input A;
input B;
input C;
input D;

output X;
output Y;

wire _1_; 
wire _2_;
wire _3_;
wire _4_;


XOR2_X1 xor1 ( .a(A), .b(B), .o(_1_) );
NAND2_X1 nand1 ( .a(_2_), .b(_3_), .o(_4_) );
OR2_X1 or1 ( .a(_3_), .b(D), .o(Y) );
INV_X1 inv1 ( .a(_1_), .o(_2_) );
INV_X1 inv2 ( .a(C), .o(_3_) );
INV_X1 inv3 ( .a(_4_), .o(X) );

