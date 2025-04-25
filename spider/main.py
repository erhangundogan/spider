from typing import Union, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
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
    if page is None:
        raise HTTPException(status_code=500, detail="Failed to crawl the URL")
    else:
        if request.store:
            connection = ValkeyConnection()
            storage = ValkeyStorage(connection)
            storage.save(page)
            return {"message": "Successfully crawled and stored", "key": page.key}
        else:
            return {"message": "Successfully crawled"}
