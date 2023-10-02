import asyncio
import json

from aiokafka import AIOKafkaConsumer
from fastapi import FastAPI, Query
from logs.logs import configure_logger
from src.service import (
    add_to_elasticsearch,
    es,
    index_name,
    search_news_in_elasticsearch,
)
from src.settings import Settings

logger = configure_logger(__name__)
settings = Settings()

app = FastAPI()

loop = asyncio.get_event_loop()
consumer = AIOKafkaConsumer(
    settings.NEWS_TOPIC,
    bootstrap_servers=settings.KAFKA_URL,
    loop=loop,
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)


async def consume_news():
    await consumer.start()
    logger.debug("Start consumer")
    try:
        async for msg in consumer:
            news_data = msg.value
            source = news_data["source"]
            title = news_data["title"]
            add_to_elasticsearch({"source": source, "title": title})
    finally:
        await consumer.stop()
        logger.debug("Stop consumer")


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    await asyncio.sleep(10)
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)
    asyncio.create_task(consume_news())


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    await consumer.stop()


@app.get("/news")
async def get_news(search: str = Query(None, title="Search Query")):
    if not search:
        return {"error": "Search parameter is required"}
    result = search_news_in_elasticsearch(search)
    if not result:
        return {"message": "No news found for the given search query"}
    return {"news": result}
