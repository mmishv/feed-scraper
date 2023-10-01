import asyncio

import pytest
from src.service import Scraper


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "parse_method",
    [
        Scraper.parse_habr,
        Scraper.parse_panorama,
        Scraper.parse_bbc,
        Scraper.parse_the_guardian,
        Scraper.parse_telegraph,
    ],
)
async def test_parse_methods(parse_method):
    result = await parse_method()
    assert "parsed_data" in result
    assert len(result["parsed_data"]) > 0
