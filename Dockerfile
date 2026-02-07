FROM python:3.11-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y 
    wget 
    gnupg 
    libnss3 
    libnspr4 
    libatk1.0-0 
    libatk-bridge2.0-0 
    libcups2 
    libdrm2 
    libxkbcommon0 
    libxcomposite1 
    libxdamage1 
    libxext6 
    libxfixes3 
    librandr2 
    libgbm1 
    libpango-1.0-0 
    libcairo2 
    libasound2 
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

CMD exec uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
