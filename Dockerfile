FROM python:3.12.3-slim

WORKDIR /src

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV ENV=${ENV}

RUN if [ "$ENV" = "dev" ]; then \
        pip install --no-cache-dir -r requirements.dev.txt ; \
    fi

COPY ./src ./src
COPY ./migrations ./migrations
COPY alembic.ini .

EXPOSE 8000

CMD sh -c "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"
