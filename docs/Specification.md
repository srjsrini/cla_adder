# 32-bit Carry Look-Ahead (CLA) Adder Specification

## Overview

Implement a 32-bit Carry Look-Ahead adder using parallel Generate and Propagate logic. A CLA adder improves speed by computing all carry bits simultaneously instead of rippling through each bit.

## Interface

| Port       | Direction | Width   | Description            |
|-----------|-----------|---------|------------------------|
| `in1`     | input     | [31:0]  | 32-bit operand A       |
| `in2`     | input     | [31:0]  | 32-bit operand B       |
| `carry_in`| input     | 1-bit   | Initial carry-in       |
| `sum`     | output    | [31:0]  | 32-bit sum result      |
| `carry_out` | output  | 1-bit   | Final carry-out        |

## Architecture Requirements

1. **Generate (G) logic:** \( G[i] = A[i] \wedge B[i] \)
2. **Propagate (P) logic:** \( P[i] = A[i] \vee B[i] \)
3. **Carry chain:**
   - \( C[0] = \text{carry\_in} \)
   - \( C[i+1] = G[i] \vee (P[i] \wedge C[i]) \)
4. **Sum logic:** \( \text{Sum}[i] = A[i] \oplus B[i] \oplus C[i] \)

## Constraints

- Purely combinational logic (no clocks or resets).
- Do not use the `+` operator for the carry chain; implement the CLA equations above.
- The 32nd carry bit is the final `carry_out`.

## Module

Implement in `sources/cla_adder.sv`. The toplevel module name used by the testbench is `cpu_wb_cla_adder` (with parameter `DATA_WID = 32`).
