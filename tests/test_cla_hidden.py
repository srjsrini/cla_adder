import cocotb
import os
import random
from pathlib import Path
from cocotb.triggers import Timer
from cocotb_tools.runner import get_runner


# =============================================================================
# Cocotb Test: CLA Validation
# =============================================================================

@cocotb.test()
async def test_cla_complete_validation(dut):
    """Comprehensive CLA test"""

    dut._log.info("=== STARTING CLA VALIDATION ===")

    width = len(dut.in1)
    mask = (1 << width) - 1

    async def verify_add(a, b, cin, tag):

        dut.in1.value = a
        dut.in2.value = b
        dut.carry_in.value = cin

        await Timer(1, unit="ns")

        full = a + b + cin

        expected_sum = full & mask
        expected_cout = (full >> width) & 1

        actual_sum = int(dut.sum.value)
        actual_cout = int(dut.carry_out.value)

        assert actual_sum == expected_sum, \
            f"FAIL [{tag}] SUM mismatch. Expected {expected_sum}, Got {actual_sum}"

        assert actual_cout == expected_cout, \
            f"FAIL [{tag}] CARRY mismatch. Expected {expected_cout}, Got {actual_cout}"

        dut._log.info(f"PASS [{tag}] -> {a} + {b} + {cin}")


    # -------------------------------------------------------------------------
    # BASIC TESTS
    # -------------------------------------------------------------------------

    await verify_add(10, 20, 0, "Basic_1")

    await verify_add(0xFFFF, 1, 0, "Overflow")


    # -------------------------------------------------------------------------
    # CARRY IN TESTS (baseline usually fails here)
    # -------------------------------------------------------------------------

    await verify_add(0, 0, 1, "Only_Cin")

    await verify_add(0x7FFF, 1, 1, "Cin_Boundary")


    # -------------------------------------------------------------------------
    # EDGE CASES
    # -------------------------------------------------------------------------

    await verify_add(0, 0, 0, "Zero")

    await verify_add(mask, mask, 1, "Absolute_Max")


    # -------------------------------------------------------------------------
    # RANDOM STRESS TEST
    # -------------------------------------------------------------------------

    dut._log.info("Starting random stress test")

    for i in range(50):

        a = random.getrandbits(width)
        b = random.getrandbits(width)
        cin = random.randint(0, 1)

        await verify_add(a, b, cin, f"Random_{i}")

    dut._log.info("=== ALL TESTS COMPLETED ===")


# =============================================================================
# Pytest Runner
# =============================================================================

def test_cla_runner():

    sim = os.getenv("SIM", "icarus")

    proj_path = Path(__file__).resolve().parent.parent

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
        test_module="test_cla_hidden"
    )
