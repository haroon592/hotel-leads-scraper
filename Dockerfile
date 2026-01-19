FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and dependencies
RUN playwright install --with-deps chromium

# Copy application files
COPY . .

# Create directories
RUN mkdir -p lead_downloads

# Expose port
EXPOSE 8080

# Run the Flask app
CMD ["python", "api_wrapper.py"]
