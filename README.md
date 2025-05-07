Spider
======

Crawler with chain requests and save data into the Valkey (open-source Redis) database

## Run locally

Clone project

```bash
uv run fastapi dev
curl --location 'http://localhost:8000/crawl' \
     --header 'Content-Type: application/json' \
     --data '{ "url": "https://www.example.com", "store": false }'
```

## Docker Compose (with save feature)

Clone project

```bash
docker-compose up --build
curl --location 'http://localhost:8000/crawl' \
     --header 'Content-Type: application/json' \
     --data '{ "url": "https://www.example.com", "store": true }'
```