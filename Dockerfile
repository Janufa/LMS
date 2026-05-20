FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev gcc git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

COPY . /app

RUN adduser --disabled-password --gecos "" appuser || true
RUN chown -R appuser:appuser /app

# Ensure entrypoint is executable
RUN chmod +x /app/entrypoint.sh

USER appuser

RUN mkdir -p /app/staticfiles

EXPOSE 8000

CMD ["./entrypoint.sh"]
