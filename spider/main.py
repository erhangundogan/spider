import asyncio
from typing import List
from crawl4ai import AsyncWebCrawler, CrawlResult
from time import sleep
from typing import Union, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
from page import Page
from connection import ValkeyConnection
from spider.spider import Spider
from spider.valkey_storage import ValkeyStorage
from enum import Enum

app = FastAPI()

class Route(Enum):
    Internal = 'internal'
    External = 'external'

class CrawlRequest(BaseModel):
    url: str
    store: Optional[bool] = Field(default=False)
    iteration: Optional[int] = Field(default=1)
    nextRoute: Optional[Route] = Field(default=Route.Internal)

@app.get("/")
async def read_root():
    return

@app.post("/crawl4ai")
async def crawl4ai(request: CrawlRequest):
    if request.url is None:
        raise HTTPException(status_code=400, detail="URL is required")
    
    async with AsyncWebCrawler() as crawler:
        # Start crawling from the given URL
        results: List[CrawlResult] = await crawler.arun(url=request.url)
        
        for i, result in enumerate(results):
            # Print the URL and the text content of the page
            print(f"Result {i+1}:")
            print(f"Success: {result.success}")
            if result.success:
                print(f"Markdown length: {len(result.markdown.raw_markdown)} chars")
                print(f"Firts 100 chars: {result.markdown.raw_markdown[:100]}...")
            else:
                print(f"Error: {result.error}")


@app.post("/crawl")
async def crawl(request: CrawlRequest):
    if request.url is None:
        raise HTTPException(status_code=400, detail="URL is required")
    
    iteration = request.iteration
    while iteration > 0:
        spider = Spider()
        page = spider.crawl(request.url)
        if page is not None:
            print(f"[{datetime.now(timezone.utc)}] Successfully crawled the page")
            print(page)
            if request.store:
                connection = ValkeyConnection()
                if connection.connect():
                    storage = ValkeyStorage()
                    storage.save(client=connection.valkey_client, page=page)
                    print(f"[{datetime.now(timezone.utc)}] Successfully stored page {page.key}")
                    del page, storage, spider
                    iteration -= 1
                    sleep(5)
                else:
                    print(f"[{datetime.now(timezone.utc)}] Failed to connect to the database")    
                    raise HTTPException(status_code=500, detail="Failed to connect to the database")
        else:
            print(f"[{datetime.now(timezone.utc)}] Failed to crawl")    
            raise HTTPException(status_code=500, detail="Failed to crawl")
        
    connection.valkey_client.close()

    return {
        "result": "success",
        "message": f"Successfully crawled {request.iteration} times."
    }
