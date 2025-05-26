FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS uv

ENV DISPLAY=0 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    UV_LOG_LEVEL=info \
    UV_VENV_DIR=/app/.venv \
    UV_VENV_PYTHON=python3.12 \
    UV_VENV_SEED=1 \
    UV_VENV_REQUIREMENTS=pyproject.toml \
    UV_VENV_REQUIREMENTS_LOCK=uv.lock

WORKDIR /app

COPY requirements.txt pyproject.toml .python-version pytest.ini uv.lock ./
COPY spider/*.py ./
COPY tests ./tests

RUN uv venv --python=python3.12 --seed
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN uv sync --locked
RUN crawl4ai-setup
RUN playwright install
RUN crawl4ai-doctor

CMD ["/app/.venv/bin/fastapi", "run", "main.py", "--port", "8000", "--host", "0.0.0.0"]