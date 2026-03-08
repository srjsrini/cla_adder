module cla_adder #(
    parameter DATA_WID = 32
)(
    input  logic [DATA_WID-1:0] in1,
    input  logic [DATA_WID-1:0] in2,
    input  logic carry_in,
    output logic [DATA_WID-1:0] sum,
    output logic carry_out
);

logic [DATA_WID-1:0] gen;
logic [DATA_WID-1:0] pro;
logic [DATA_WID:0] carry_tmp;

// WRONG initialization (intentional bug)
assign carry_tmp[0] = 1'b0;

generate
    genvar i;
    for(i = 0; i < DATA_WID; i++) begin : cla_logic

        // generate
        assign gen[i] = in1[i] & in2[i];

        // WRONG propagate definition
        assign pro[i] = in1[i] ^ in2[i];

        // WRONG carry equation
        assign carry_tmp[i+1] = gen[i] | pro[i];

        // sum calculation
        assign sum[i] = in1[i] ^ in2[i] ^ carry_tmp[i];

    end
endgenerate

assign carry_out = carry_tmp[DATA_WID];

endmodule


