FROM python:3.11-alpine

WORKDIR /app

COPY webhook_lens.py .

RUN chmod +x webhook_lens.py

EXPOSE 8000

CMD ["python3", "webhook_lens.py", "-p", "8000"]
