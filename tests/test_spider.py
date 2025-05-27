import asyncio
import pytest
import pytest_asyncio
from spider.spider import Spider

@pytest_asyncio.fixture
async def page():
    spider = Spider()
    return await spider.crawl("https://example.com", use_crawl4ai=False)

async def test_is_external_link(page):
    assert "https://www.iana.org/domains/example" in page.links_external

async def test_base_url(page):
    assert page.base_url == "https://example.com"
