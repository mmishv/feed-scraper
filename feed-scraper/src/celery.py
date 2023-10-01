from celery import Celery
from celery.schedules import crontab
from src.settings import Settings

settings = Settings()
app = Celery(
    "feed-scraper",
    broker_url=settings.REDIS_URL,
    result_backend=settings.REDIS_URL,
    include=["src.producer_tasks"],
)
app.conf.timezone = "Europe/Moscow"
app.conf.beat_schedule = {
    "scrape-and-push-news-daily": {
        "task": "src.producer_tasks.scrape_and_push_news_task",
        "schedule": crontab(minute=0, hour=0),
    },
}
