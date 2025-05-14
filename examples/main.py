import asyncio

from yamusicrpc import ActivityManager


async def main() -> None:
    activity_manager = ActivityManager()
    await activity_manager.start()

asyncio.run(main())
