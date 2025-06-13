FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir httpx mcp[cli] python-dotenv

COPY . .

ENV PORT=10000

CMD ["python", "main.py"]
