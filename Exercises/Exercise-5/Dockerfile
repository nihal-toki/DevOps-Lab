
# Use an official Python runtime
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy the application
COPY app.py /app/

# Install Flask compatible with Python 3.8
RUN pip install --no-cache-dir "Flask==2.2.5" "Werkzeug==2.2.3"

# Expose port 5000
EXPOSE 5000

# Start the Flask application
CMD ["python", "app.py"]
