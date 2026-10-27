from __future__ import annotations

from collections.abc import Awaitable, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler


class SchedulerBackend:
    def start(self) -> None:
        raise NotImplementedError

    def shutdown(self) -> None:
        raise NotImplementedError

    def add_interval_job(self, coro: Callable[[], Awaitable[None]], seconds: int, job_id: str) -> None:
        raise NotImplementedError


class APSchedulerBackend(SchedulerBackend):
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        self.scheduler.start()

    def shutdown(self) -> None:
        self.scheduler.shutdown(wait=False)

    def add_interval_job(self, coro: Callable[[], Awaitable[None]], seconds: int, job_id: str) -> None:
        self.scheduler.add_job(coro, "interval", seconds=seconds, id=job_id, replace_existing=True)
