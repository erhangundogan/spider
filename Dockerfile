FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS uv

COPY requirements.txt pyproject.toml .python-version pytest.ini uv.lock /app/
COPY spider/*.py /app/
COPY tests /app/tests

WORKDIR /app

RUN uv sync --frozen --no-cache
CMD ["/app/.venv/bin/fastapi", "run", "main.py", "--port", "8000", "--host", "0.0.0.0"]