Spider
======

Crawler with chain requests and save data into the Valkey (open-source Redis) database

## Docker Compose (with save feature)

Clone project

```bash
docker-compose up --build
curl --location 'http://localhost:8000/crawl' \
     --header 'Content-Type: application/json' \
     --data '{ "url": "https://www.example.com", "store": true }'

# OR alternatively you can use Crawl4AI
curl --location 'http://localhost:8000/crawl4ai' \
     --header 'Content-Type: application/json' \
     --data '{ "url": "https://www.example.com", "store": true }'
```