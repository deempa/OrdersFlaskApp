FROM python:3.11.2-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--capture-output", "--access-logfile '-'", "--error-logfile '-'"]

# CMD [ "python3", "app.py" ]