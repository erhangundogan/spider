from typing import Union, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
from page import Page
from connection import ValkeyConnection
from spider.spider import Spider
from storage import ValkeyStorage

app = FastAPI()

class CrawlRequest(BaseModel):
    url: str
    store: Optional[bool] = Field(default=False)

@app.get("/")
def read_root():
    return

@app.post("/crawl")
async def crawl(request: CrawlRequest):
    if request.url is None:
        raise HTTPException(status_code=400, detail="URL is required")

    spider = Spider()
    page = spider.crawl(request.url)
    if page is not None:
        print(f"[{datetime.now(timezone.utc)}] Successfully crawled the page")
        print(page)
        connection = ValkeyConnection()
        result = connection.connect()
        if result and request.store:
            storage = ValkeyStorage()
            storage.save(client=connection.valkey_client, page=page)
            print(f"[{datetime.now(timezone.utc)}] Successfully stored page {page.key}")
            del page, storage, spider
            connection.valkey_client.close()
        return {
            "result": "success",
            "message": "Successfully crawled and stored"
        }
    else:
        print(f"[{datetime.now(timezone.utc)}] Failed to crawl or store")    
        raise HTTPException(status_code=500, detail="Failed to crawl/store the page")