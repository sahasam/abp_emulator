# Emulate FPGA registers of ABP verilog implementation for Dugan's visualizations
import asyncio
import logging
import random
import threading
import time

# Global variables for simulation ticks and timing
tick = 0
ticks_per_transmission = 150
ticks_per_transit = 150
tick_period_ns = 8

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ABPMock:
    def __init__(self):
        # Initialize simulation state
        self.sim_state = {
            'bob.event_counter': 0,
            'bob.data_register': 0,
            'alice.event_counter': 0,
            'alice.data_register': 0
        }

        # Event signaling that sender operation is done
        self.data_to_send = random.randint(0, 50)
        self.sender_op_done = asyncio.Event()
        self.loop = asyncio.new_event_loop()
        self.event_loop_thread = threading.Thread(target=self.start_event_loop, daemon=True)
        self.event_loop_thread.start()

    def poll_state(self):
        """Poll the current simulation state."""
        global tick
        return (tick, self.sim_state)
    
    def set_data_register(self, number):
        self.data_to_send = number


    def kill(self):
        """Stop the event loop."""
        asyncio.run_coroutine_threadsafe(self.shutdown(), self.loop)
        self.event_loop_thread.join()
        logger.info("Event loop stopped")

    async def shutdown(self):
        """Shutdown all tasks and stop the event loop."""
        tasks = [t for t in asyncio.all_tasks(self.loop) if t is not asyncio.current_task(self.loop)]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self.loop.stop()

    async def send_data(self):
        """Simulate data sending process."""
        global tick
        next_trigger_time = tick + ticks_per_transmission

        while True:
            if tick >= next_trigger_time:
                next_trigger_time += ticks_per_transmission
                self.sim_state['alice.event_counter'] += 1
                self.sim_state['alice.data_register'] = self.data_to_send
                self.data_to_send += 1

                logger.debug(f"send_data() - new data sent at tick {tick}: {self.data_to_send}")
                self.sender_op_done.set()
            await asyncio.sleep(0)  # Yield control to event loop

    async def recv_data(self, start_time):
        """Simulate data receiving process."""
        global tick
        next_trigger_time = start_time + ticks_per_transit

        while True:
            if tick >= next_trigger_time:
                self.sim_state['bob.event_counter'] += 1
                self.sim_state['bob.data_register'] = self.sim_state['alice.data_register']

                logger.debug(f"recv_data() - sender data copied at {tick}: {self.sim_state['bob.data_register']}")
                break
            await asyncio.sleep(0)  # Yield control to event loop

    async def recv_scheduler(self):
        """Schedule receiving tasks based on sender operation completion."""
        global tick
        while True:
            await self.sender_op_done.wait()
            asyncio.create_task(self.recv_data(tick))
            self.sender_op_done.clear()

    async def fpga_clock(self):
        """Simulate FPGA clock ticks."""
        global tick
        while True:
            tick += 1
            await asyncio.sleep(0)

    def start_event_loop(self):
        """Start the asyncio event loop."""
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.main_loop())
        except asyncio.CancelledError:
            pass
        finally:
            self.loop.close()

    async def main_loop(self):
        """Main loop to run all tasks concurrently."""
        await asyncio.gather(
            self.send_data(),
            self.fpga_clock(),
            self.recv_scheduler(),
        )
    


if __name__ == "__main__":
    mock = ABPMock()

    for _ in range(10):
        time.sleep(0.1)
        print(mock.poll_state())
    
    mock.kill()