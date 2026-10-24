
FROM python:3.9-slim

WORKDIR /app

RUN pip install --no-cache-dir flask==3.1.3

COPY app.py .

EXPOSE 15000

CMD ["python", "app.py"]
