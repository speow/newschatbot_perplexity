import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from services.scheduler.jobs import send_digest


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_digest, "cron", hour=19, minute=21)
    scheduler.start()

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler was stopped by CTRL + C!")


if __name__ == "__main__":
    asyncio.run(main())
