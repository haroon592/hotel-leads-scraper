FROM python:3.11-slim

# Install dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium

# Copy application files
COPY . .

# Create directories
RUN mkdir -p lead_downloads

# Expose port
EXPOSE 8080

# Run the Flask app
CMD ["python", "api_wrapper.py"]
