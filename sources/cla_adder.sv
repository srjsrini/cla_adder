`timescale 1ns/1ps

module cpu_wb_cla_adder #(
    parameter DATA_WID = 32
)(
    input  logic [DATA_WID-1:0] in1,
    input  logic [DATA_WID-1:0] in2,
    input  logic                carry_in,
    output logic [DATA_WID-1:0] sum,
    output logic                carry_out
);

    logic [DATA_WID-1:0] gen;
    logic [DATA_WID-1:0] pro;
    logic [DATA_WID:0]   carry_tmp;

    // BUG: Hardcoded to 0. Passes if carry_in is 0, fails if 1.
    generate
    // TODO: Implement Generate/Propagate logic and Sum calculation here
    endgenerate

    assign carry_out = carry_tmp[DATA_WID];
    assign carry_tmp[0] = 1'b0;
    endmodule
