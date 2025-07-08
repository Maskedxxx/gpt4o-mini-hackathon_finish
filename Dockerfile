FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Create logs directory
RUN mkdir -p LOGS

# Expose port
EXPOSE 3000

# Default command (can be overridden)
CMD ["python", "-m", "src.web_app.unified_app.main"]