
# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Flask application
COPY app.py .

# Expose Flask port
EXPOSE 5001

# Start Flask application
CMD ["python", "app.py"]
