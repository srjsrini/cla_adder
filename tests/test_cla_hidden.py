import cocotb
from cocotb.triggers import Timer
import random
import os
from pathlib import Path

DATA_WID = 32


# -------------------------------------------------
# Anti-cheat check (prevents trivial '+' solutions)
# -------------------------------------------------
proj_path = Path(__file__).resolve().parent.parent

with open(proj_path / "sources/cla_adder.sv") as f:
    code = f.read()

assert "generate" in code, "Design must use generate logic"


# -------------------------------------------------
# Helper function for verification
# -------------------------------------------------
async def verify_add(dut, a, b, cin, name):

    dut.in1.value = a
    dut.in2.value = b
    dut.carry_in.value = cin

    await Timer(1, units="ns")

    full = a + b + cin
    mask = (1 << DATA_WID) - 1

    expected_sum = full & mask
    expected_cout = (full >> DATA_WID) & 1

    dut_sum = int(dut.sum.value)
    dut_cout = int(dut.carry_out.value)

    assert dut_sum == expected_sum, (
        f"{name} SUM FAIL: a={a:x} b={b:x} cin={cin} "
        f"expected={expected_sum:x} got={dut_sum:x}"
    )

    assert dut_cout == expected_cout, (
        f"{name} CARRY FAIL: expected={expected_cout} got={dut_cout}"
    )


# -------------------------------------------------
# Main Cocotb Test
# -------------------------------------------------
@cocotb.test()
async def test_cla_complete_validation(dut):

    # Directed tests
    await verify_add(dut, 0, 0, 0, "all_zero")
    await verify_add(dut, 0, 0, 1, "only_carry")
    await verify_add(dut, 1, 1, 0, "small_add")
    await verify_add(dut, 0xFFFFFFFF, 0x0, 0, "max_plus_zero")
    await verify_add(dut, 0xFFFFFFFF, 0x1, 0, "max_plus_one")

    # Carry chain stress patterns
    await verify_add(dut, 0xAAAAAAAA, 0x55555555, 0, "propagate_pattern")
    await verify_add(dut, 0xFFFFFFFF, 0x00000001, 0, "carry_chain")
    await verify_add(dut, 0x7FFFFFFF, 0x00000001, 0, "overflow_boundary")
    await verify_add(dut, 0x80000000, 0x80000000, 0, "signed_edge")

    # Random tests
    for i in range(300):

        a = random.getrandbits(DATA_WID)
        b = random.getrandbits(DATA_WID)
        cin = random.getrandbits(1)

        await verify_add(dut, a, b, cin, f"random_{i}")


# -------------------------------------------------
# REQUIRED: Pytest wrapper
# -------------------------------------------------
def test_problem_runner():

    import os
    from cocotb_tools.runner import get_runner

    sim = os.getenv("SIM", "icarus")

    proj_path = Path(__file__).resolve().parent.parent

    sources = [
        proj_path / "sources/cla_adder.sv",
    ]

    runner = get_runner(sim)

    runner.build(
        sources=sources,
        hdl_toplevel="cla_adder",
        always=True,
    )

    runner.test(
        hdl_toplevel="cla_adder",
        test_module="test_cla_hidden",
    )
