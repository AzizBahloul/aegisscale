FROM python:3.11-slim-bookworm

# Apply security patches to reduce vulnerabilities
RUN apt-get update && apt-get upgrade -y && apt-get install --only-upgrade -y openssl libssl3 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# bring OS packages up to date to remove known vulnerabilities
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# upgrade pip to latest patch release
RUN pip install --upgrade pip

COPY setup.py requirements.txt ./
# Install package (and its dependencies)
RUN pip install --no-cache-dir .

COPY . .

EXPOSE 8000
EXPOSE 8001

CMD ["aegisscale", "--host", "0.0.0.0", "--port", "8000"]
