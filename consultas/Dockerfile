FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt  .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5003

COPY app.py  .
COPY databasesc.py .

CMD [ "python", "app.py" ]
