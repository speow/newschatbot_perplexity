import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from services.scheduler.jobs import send_digest

from config import DIGEST_HOURS, DIGEST_MINUTES


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_digest, "cron", DIGEST_HOURS, DIGEST_MINUTES)
    scheduler.start()
    print("Digest scheduler was started.")

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler was stopped by CTRL + C!")


if __name__ == "__main__":
    asyncio.run(main())
