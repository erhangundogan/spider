import pytest
from spider.spider import Spider

@pytest.fixture
def page():
    spider = Spider()
    return spider.crawl("https://example.com")

def test_is_external_link(page):
    assert "https://www.iana.org/domains/example" in page.links_external

def test_base_url(page):
    assert page.base_url == "https://example.com"
