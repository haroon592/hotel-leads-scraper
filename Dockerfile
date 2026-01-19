FROM python:3.11-slim

# Install Firefox and dependencies
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directories
RUN mkdir -p lead_downloads

# Expose port
EXPOSE 8080

# Run the Flask app
CMD ["python", "api_wrapper.py"]
