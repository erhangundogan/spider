Spider
======

Simple crawler to scrap web pages.

## Run (Docker)

```bash
docker run -it --rm ghcr.io/erhangundogan/spider:latest https://www.example.com
```

## Run locally

- Clone project

- Install dependencies

```bash
pip install -r requirements.txt
```

- Run project with extra argument to scrap address

```bash
python spider/spider.py https://www.example.com
```

