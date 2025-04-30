import asyncio
import threading

class AsyncWorker:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run_task(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

if __name__ == "__main__":
    # Example usage
    async_worker = AsyncWorker()

    async def example_task():
        print("Running task in the event loop")
        await asyncio.sleep(1)
        print("Task completed")

    # Run the example task
    async_worker.run_task(example_task())
