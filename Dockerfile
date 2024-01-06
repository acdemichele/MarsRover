FROM python:3.10.11

WORKDIR /app


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt

COPY app app

EXPOSE 8000
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
