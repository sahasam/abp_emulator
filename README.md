# ABP FPGA Register Emulator

Sahas Munamala - Sat Jun 15, 2024

This project emulates FPGA registers for an Alternating Bit Protocol (ABP) Verilog implementation. The emulator is designed for use with Dugan's visualizations, simulating the behavior of the ABP in a Python environment using asyncio and threading.
Features

    Simulates FPGA registers and their state changes over time.
    Emulates data transmission and reception between Alice and Bob.
    Utilizes asyncio for asynchronous event handling.
    Configurable tick periods and transmission intervals.

Requirements

    Python 3.7 or higher
    asyncio library
    threading library
    logging library

```
python3 -m venv env
source ./env/bin/activate
pip install -r requirements.txt
```