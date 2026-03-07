import cocotb
import os
import random
from pathlib import Path
from cocotb.triggers import Timer
from cocotb_tools.runner import get_runner

# ==============================================================================
# ✅ Cocotb Test: Comprehensive CLA Validation
# ==============================================================================
@cocotb.test()
async def test_cla_complete_validation(dut):
    """
    Complete CLA test: 
    1. Basic Addition (Baseline usually passes)
    2. Carry-In verification (Baseline usually FAILS here)
    3. Maximum value/Overflow check
    4. Random stress testing (50 iterations)
    """
    
    dut._log.info("=== STARTING CLA COMPREHENSIVE VALIDATION ===")

    # Helper function to perform a self-checking addition
    async def verify_add(a, b, cin, tag):
        # Apply inputs
        dut.in1.value = a
        dut.in2.value = b
        dut.carry_in.value = cin
        
        # CLA is combinational logic, so we just need a tiny delay 
        # for the simulator to propagate the values.
        await Timer(1, units="ns")
        
        # Calculate expected result using Python (Our Golden Model)
        # Using 32-bit width by default, but matches your RTL parameter
        width = len(dut.in1) 
        mask = (1 << width) - 1
        
        full_res = a + b + cin
        expected_sum = full_res & mask
        expected_cout = (full_res >> width) & 0x1
        
        # Read actual values from DUT
        actual_sum = int(dut.sum.value)
        actual_cout = int(dut.carry_out.value)
        
        # Assertions (The "Hidden" part that grades the AI)
        assert actual_sum == expected_sum, \
            f"✗ FAIL [{tag}]: Sum Mismatch! {a}+{b}+cin:{cin}. Exp: {expected_sum}, Got: {actual_sum}"
        
        assert actual_cout == expected_cout, \
            f"✗ FAIL [{tag}]: Carry-Out Mismatch! Exp: {expected_cout}, Got: {actual_cout}"
        
        dut._log.info(f"✓ PASS [{tag}]: {a} + {b} + {cin} = {actual_sum} (Cout: {actual_cout})")

    # ----- TEST 1: Basic Operations (Cin=0) -----
    # These are similar to your Verilog testbench cases
    await verify_add(16'd10, 16'd20, 0, "Basic_1")
    await verify_add(16'hFFFF, 16'h0001, 0, "Max_Overflow")

    # ----- TEST 2: Carry-In Verification -----
    # This specifically catches the 1'b0 bug in your baseline
    await verify_add(16'd0, 16'd0, 1, "Only_Cin")
    await verify_add(16'h7FFF, 16'h0001, 1, "Cin_Boundary")

    # ----- TEST 3: Edge Cases -----
    await verify_add(0, 0, 0, "Zero_Check")
    await verify_add(mask := (1 << len(dut.in1)) - 1, mask, 1, "Absolute_Max")

    # ----- TEST 4: Randomized Stress Test -----
    # 50 iterations of random data to ensure no logic holes
    dut._log.info("=== STARTING RANDOM STRESS TEST (50 iterations) ===")
    for i in range(50):
        r_a = random.getrandbits(len(dut.in1))
        r_b = random.getrandbits(len(dut.in1))
        r_c = random.randint(0, 1)
        await verify_add(r_a, r_b, r_c, f"Random_{i}")

    dut._log.info("=== ALL CLA TESTS PASSED SUCCESSFULLY ===")

# ==============================================================================
# ✅ REQUIRED: Pytest runner wrapper
# ==============================================================================
def test_cla_runner():
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    
    # Define source files for the simulator
    sources = [
        proj_path / "sources" / "cla_adder.sv",
    ]
    
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="cpu_wb_cla_adder",
        always=True,
    )
    
    runner.test(
        hdl_toplevel="cpu_wb_cla_adder", 
        test_module="test_cla_hidden", 
        waves=True 
    )
