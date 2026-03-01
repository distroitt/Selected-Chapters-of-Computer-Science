FROM python:3.11-slim

WORKDIR /app

COPY circle.py .
COPY square.py .
COPY main.py .

ENV SQUARE_SIDE=5
ENV CIRCLE_RADIUS=3

CMD ["python", "main.py"]
