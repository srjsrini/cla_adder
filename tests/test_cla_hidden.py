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
    """Verify CLA logic: Basic sums, Carry-In influence, and Overflow (Carry-Out)."""
    
    dut._log.info("=== STARTING CLA COMPREHENSIVE VALIDATION ===")

    # Helper function to perform a check
    async def check_addition(a, b, cin, description):
        dut.in1.value = a
        dut.in2.value = b
        dut.carry_in.value = cin
        
        # Combinational logic needs a small timer delay to propagate
        await Timer(1, units="ns")
        
        # Golden Model (Python integers)
        full_result = a + b + cin
        expected_sum = full_result & 0xFFFFFFFF
        expected_cout = (full_result >> 32) & 0x1
        
        # Verify Sum
        actual_sum = int(dut.sum.value)
        actual_cout = int(dut.carry_out.value)
        
        assert actual_sum == expected_sum, \
            f"✗ FAIL [{description}]: Sum Mismatch! {a} + {b} + {cin}. Exp: {expected_sum}, Got: {actual_sum}"
        
        assert actual_cout == expected_cout, \
            f"✗ FAIL [{description}]: Carry-Out Mismatch! Exp: {expected_cout}, Got: {actual_cout}"
        
        dut._log.info(f"✓ PASS [{description}]: {a} + {b} + {cin} = {actual_sum} (Cout: {actual_cout})")

    # ===== TEST 1: Basic Addition (No Carry-In) =====
    await check_addition(10, 20, 0, "Basic Small Sum")
    
    # ===== TEST 2: Impact of Carry-In =====
    # This specifically targets the baseline bug where carry_in is ignored
    await check_addition(5, 5, 1, "Carry-In Influence")
    
    # ===== TEST 3: Max Values (Overflow Test) =====
    await check_addition(0xFFFFFFFF, 1, 0, "All Ones + 1")
    await check_addition(0xFFFFFFFF, 0xFFFFFFFF, 1, "Max Possible Sum")

    # ===== TEST 4: Zero States =====
    await check_addition(0, 0, 0, "All Zeros")
    await check_addition(0, 0, 1, "Only Carry-In")

    # ===== TEST 5: Random Stress Test =====
    dut._log.info("=== STARTING RANDOM STRESS TEST (50 Iterations) ===")
    for i in range(50):
        a = random.randint(0, 0xFFFFFFFF)
        b = random.randint(0, 0xFFFFFFFF)
        cin = random.randint(0, 1)
        await check_addition(a, b, cin, f"Random_{i}")

    dut._log.info("=== ALL CLA TESTS PASSED SUCCESSFULLY ===")

# ==============================================================================
# ✅ REQUIRED: Pytest runner wrapper
# ==============================================================================
def test_cla_runner():
    """Configures the simulation environment for the CLA Adder."""
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    
    # Define source files
    sources = [
        proj_path / "sources" / "cla_adder.sv",
    ]
    
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="cpu_wb_cla_adder",  # Matches your module name
        always=True,
    )
    
    runner.test(
        hdl_toplevel="cpu_wb_cla_adder", 
        test_module="test_cla_hidden",   # The name of this file
        waves=True                       # Enables .vcd generation
    )
