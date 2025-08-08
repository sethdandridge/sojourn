FROM python:3.13.5-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache --requirement requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=1

ENTRYPOINT ["gunicorn", "-w", "5", "-b", "0.0.0.0:80", "--max-requests", "1000", "--max-requests-jitter", "50", "--preload", "app:create_app()"]

LABEL org.opencontainers.image.source=https://github.com/sethdandridge/sojourn

