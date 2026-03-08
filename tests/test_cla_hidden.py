import cocotb
from cocotb.triggers import Timer
import random

DATA_WID = 32


async def verify_add(dut, a, b, cin):

    dut.in1.value = a
    dut.in2.value = b
    dut.carry_in.value = cin

    await Timer(1, units="ns")

    full = a + b + cin
    mask = (1 << DATA_WID) - 1

    expected_sum = full & mask
    expected_cout = (full >> DATA_WID) & 1

    assert int(dut.sum.value) == expected_sum, \
        f"SUM mismatch: {a}+{b}+{cin}"

    assert int(dut.carry_out.value) == expected_cout, \
        f"COUT mismatch: {a}+{b}+{cin}"


@cocotb.test()
async def cla_hidden_test(dut):

    # -----------------------------
    # Basic correctness tests
    # -----------------------------
    await verify_add(dut, 0, 0, 0)
    await verify_add(dut, 0, 0, 1)
    await verify_add(dut, 1, 1, 0)
    await verify_add(dut, 15, 10, 0)

    # -----------------------------
    # Edge cases
    # -----------------------------
    await verify_add(dut, 0xFFFFFFFF, 0, 0)
    await verify_add(dut, 0xFFFFFFFF, 1, 0)
    await verify_add(dut, 0xFFFFFFFF, 0, 1)

    # -----------------------------
    # 🔥 Carry Propagation Trap
    # -----------------------------
    # Requires long carry chain
    await verify_add(dut, 0x7FFFFFFF, 1, 0)

    # Full 32-bit propagation
    await verify_add(dut, 0xFFFFFFFF, 0, 1)

    # Near overflow propagation
    await verify_add(dut, 0x7FFFFFFE, 1, 1)

    # Alternating propagation pattern
    await verify_add(dut, 0xAAAAAAAA, 0x55555555, 0)

    # Long propagate chain
    await verify_add(dut, 0x0FFFFFFF, 1, 0)

    # -----------------------------
    # Random stress tests
    # -----------------------------
    for _ in range(200):

        a = random.getrandbits(32)
        b = random.getrandbits(32)
        cin = random.getrandbits(1)

        await verify_add(dut, a, b, cin)


# pytest wrapper
def test_problem_runner():

    import os
    from pathlib import Path
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
