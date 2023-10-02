import asyncio

import aiohttp
from bs4 import BeautifulSoup
from logs.logs import configure_logger

logger = configure_logger(__name__)


class SingletonSession:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.session = aiohttp.ClientSession()
        return cls._instance

    @property
    def instance(self):
        return self._instance


class Scraper:
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

    @staticmethod
    async def __fetch_site(source, url, el, class_name, child=None):
        try:
            headers = {"User-Agent": Scraper.USER_AGENT}
            async with SingletonSession().instance.session.get(
                url, headers=headers
            ) as response:
                response.raise_for_status()
                html_content = await response.text()
                soup = BeautifulSoup(html_content, "html.parser")
                article_titles = []
                articles = soup.find_all(el, class_=class_name)
                for article in articles:
                    title = (
                        article.find(child).text.strip()
                        if child
                        else article.text.strip()
                    )
                    article_titles.append(title)
                return {"source": source, "parsed_data": article_titles}
        except aiohttp.ClientError as e:
            error_message = f"An error occurred during the request: {str(e)}"
            logger.error(error_message)
            return {"error": error_message}
        except AttributeError as e:
            error_message = f"An error occurred while parsing the content: {str(e)}"
            logger.error(error_message)
            return {"error": error_message}

    @staticmethod
    async def parse_habr():
        url = "https://habr.com/ru/"
        return await Scraper.__fetch_site("habr.com", url, "h2", "tm-title tm-title_h2")

    @staticmethod
    async def parse_panorama():
        url = "https://panorama.pub/"
        return await Scraper.__fetch_site(
            "panorama.pub",
            url,
            "div",
            "pl-2 pr-1 text-sm basis-auto self-center",
            "div",
        )

    @staticmethod
    async def parse_bbc():
        url = "https://www.bbc.com/news"
        return await Scraper.__fetch_site(
            "bbc.com",
            url,
            "h3",
            "gs-c-promo-heading__title gel-pica-bold nw-o-link-split__text",
        )

    @staticmethod
    async def parse_the_guardian():
        url = "https://www.theguardian.com/world"
        return await Scraper.__fetch_site(
            "theguardian.com", url, "span", "show-underline dcr-adlhb4"
        )

    @staticmethod
    async def parse_telegraph():
        url = "https://www.telegraph.co.uk/culture/"
        return await Scraper.__fetch_site(
            "telegraph.co", url, "span", "list-headline__text", "span"
        )
