Spider
======

Crawler with chain requests and save data into Valkey (open-source Redis)

## Run locally

Clone project

```bash
pip install -r requirements.txt
cd spider
fastapi run main.py
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