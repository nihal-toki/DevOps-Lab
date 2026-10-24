FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY delivery_monitoring/delivery_metrics.py delivery_monitoring/delivery_metrics.py
COPY run_metrics.py test_metrics.py ./
EXPOSE 8000
CMD ["python", "-u", "run_metrics.py"]
