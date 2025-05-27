import asyncio
import json
from time import sleep
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
from enum import Enum
from .page import Page
from .connection import ValkeyConnection
from .spider import Spider
from .valkey_storage import ValkeyStorage

app = FastAPI()

class Route(Enum):
    Internal = 'internal'
    External = 'external'

class CrawlRequest(BaseModel):
    url: str
    store: Optional[bool] = Field(default=False)
    iteration: Optional[int] = Field(default=1)
    nextRoute: Optional[Route] = Field(default=Route.Internal)

async def process_crawling(request: CrawlRequest, use_crawl4ai):
    connection = ValkeyConnection() if request.store else None
    iteration = request.iteration
    last_page = None
    while iteration > 0:
        spider = Spider()
        page = await spider.crawl(request.url, use_crawl4ai)
        if page is not None:
            last_page = page
            print(f"[{datetime.now(timezone.utc)}] Successfully crawled the page")
            print(page)
            iteration -= 1

            if request.store is not None and request.store:
                if connection.connect():
                    storage = ValkeyStorage()
                    storage.save(client=connection.valkey_client, page=page)
                    print(f"[{datetime.now(timezone.utc)}] Successfully stored page {page.key}")
                    del page, storage, spider
                    connection.valkey_client.close()
                    sleep(5)
                else:
                    print(f"[{datetime.now(timezone.utc)}] Failed to connect to the database")    
                    raise HTTPException(status_code=500, detail="Failed to connect to the database")

        else:
            print(f"[{datetime.now(timezone.utc)}] Failed to crawl")    
            raise HTTPException(status_code=500, detail="Failed to crawl")
        
    if connection is not None and connection.valkey_client is not None:
        connection.valkey_client.close()

    return last_page

@app.get("/")
async def read_root():
    return

@app.post("/crawl4ai")
async def crawl4ai(request: CrawlRequest):
    if request.url is None:
        raise HTTPException(status_code=400, detail="URL is required")
    
    response = await process_crawling(request, use_crawl4ai=True)
    result = json.loads(response.to_json())

    return {
        "result": result,
        "message": "Successfully crawled"
    }

@app.post("/crawl")
async def crawl(request: CrawlRequest):
    if request.url is None:
        raise HTTPException(status_code=400, detail="URL is required")
    
    response = await process_crawling(request, use_crawl4ai=False)
    result = json.loads(response.to_json())

    return {
        "result": result,
        "message": "Successfully crawled"
    }
