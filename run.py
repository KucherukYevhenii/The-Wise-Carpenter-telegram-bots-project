import asyncio
import signal
from bots.user_bot.main import main as user_main
from bots.admin_bot.main import main as admin_main

async def main():
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    task1 = asyncio.create_task(user_main())
    task2 = asyncio.create_task(admin_main())

    await stop_event.wait()

    task1.cancel()
    task2.cancel()
    await asyncio.gather(task1, task2, return_exceptions=True)
    print("\nОбидва боти зупинені.")

if __name__ == "__main__":
    asyncio.run(main())