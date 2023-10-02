from fastapi import FastAPI
from src.producer_tasks import scrape_and_push_news_task

app = FastAPI()


@app.get("/test-trigger")
async def test_scrape_news():
    scrape_and_push_news_task.delay()
