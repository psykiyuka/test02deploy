import logging

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger("shop")

scheduler = BackgroundScheduler(
    timezone="Asia/Shanghai",
    job_defaults={
        "coalesce": True,
        "max_instances": 1,
        "misfire_grace_time": 60,
    },
)


def start_scheduler():
    scheduler.start()
    logger.info("[Scheduler] 定时任务调度器已启动")


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[Scheduler] 定时任务调度器已关闭")