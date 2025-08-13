FROM python:3.11-slim-bullseye

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# bring OS packages up to date to remove known vulnerabilities
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# upgrade pip to latest patch release
RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
EXPOSE 8001

CMD ["uvicorn", "aegisscale.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
