FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD gunicorn dreamphish.wsgi:application --bind 0.0.0.0:${PORT:-8000}
