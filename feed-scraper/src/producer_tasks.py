import asyncio
import json

from aiokafka import AIOKafkaProducer
from logs.logs import configure_logger
from src.celery import app
from src.service import Scraper
from src.settings import Settings

logger = configure_logger(__name__)
settings = Settings()
sources = [
    Scraper.parse_telegraph,
    Scraper.parse_panorama,
    Scraper.parse_habr,
    Scraper.parse_the_guardian,
    Scraper.parse_bbc,
]
loop = asyncio.get_event_loop()
producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_URL, loop=loop)


@app.task
def scrape_and_push_news_task():
    logger.info("Start scrape news task")
    return loop.run_until_complete(scrape_and_push_news())


async def scrape_and_push_news():
    await producer.start()
    logger.debug("Start producer")
    try:
        for source in sources:
            news_data = await source()
            for news in news_data["parsed_data"]:
                await producer.send_and_wait(
                    settings.NEWS_TOPIC,
                    value=json.dumps(
                        {"source": news_data["source"], "title": news}
                    ).encode("utf-8"),
                )
            logger.info(f"{len(news_data['parsed_data'])} news were sent")
    finally:
        await producer.stop()
        logger.debug("Stop producer")
