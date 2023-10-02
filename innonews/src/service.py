from elasticsearch import Elasticsearch
from logs.logs import configure_logger
from src.settings import Settings

logger = configure_logger(__name__)
settings = Settings()

es = Elasticsearch(
    [{"host": settings.ELASTIC_HOST, "port": settings.ELASTIC_PORT, "scheme": "http"}]
)
index_name = "news"


def search_news_in_elasticsearch(search_query):
    logger.info(f"Start searching {search_query}")
    result = es.search(
        index=index_name, body={"query": {"match": {"title": search_query}}}
    )
    relevant_news = []
    for hit in result["hits"]["hits"]:
        news_data = hit["_source"]
        relevant_news.append(news_data)
    logger.info(f"Return {len(relevant_news)} results")
    return relevant_news


def add_to_elasticsearch(news_document):
    existing_news = search_news_in_elasticsearch(news_document["title"])
    if not existing_news or all(
        x["source"] != news_document["source"] for x in existing_news
    ):
        es.index(index=index_name, doc_type="doc", body=news_document)
        logger.info(f'Add news from {news_document["source"]}')
        return
    logger.info(f'News from {news_document["source"]} already exists, skipped')
