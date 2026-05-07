FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl unzip nodejs npm && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3000 8800

HEALTHCHECK --interval=30s --timeout=5s --start-period=45s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8800/ping')" || exit 1

CMD ["reflex", "run"]
