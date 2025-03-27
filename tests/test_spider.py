import pytest
from spider.spider import Spider

@pytest.fixture
def spider():
    return Spider("https://example.com")

def test_is_internal_link(spider):
    assert spider.is_internal_link("https://example.com/page") is True
    assert spider.is_internal_link("https://external.com") is False

def test_base_url(spider):
    assert spider.base_url == "https://example.com"

def test_initial_links(spider):
    assert isinstance(spider.links, dict)
    assert "internal" in spider.links
    assert "external" in spider.links
    assert "skipped" in spider.links
    assert "exposed" in spider.links
