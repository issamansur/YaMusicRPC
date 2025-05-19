import asyncio
import threading

class AsyncTaskManager:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.task = None
        self.stop_event = None
        self.thread.start()

    def start(self, coro_func):
        if self.task and not self.task.done():
            print("[TaskManager] Task already running")
            return

        def schedule():
            self.stop_event = asyncio.Event()

            async def wrapped():
                try:
                    await coro_func(self.stop_event)
                except asyncio.CancelledError:
                    print("[TaskManager] Task was cancelled")

            self.task = asyncio.create_task(wrapped())

        self.loop.call_soon_threadsafe(schedule)

    def stop(self):
        if self.task and not self.task.done():
            def stop_event_set():
                if self.stop_event:
                    self.stop_event.set()
                    print("[TaskManager] Stop event was sent")

            self.loop.call_soon_threadsafe(stop_event_set)

    def is_running(self):
        return self.task is not None and not self.task.done()