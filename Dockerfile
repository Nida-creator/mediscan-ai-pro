FROM python:3.11-slim

WORKDIR /app

COPY requirements_flask.txt .
RUN pip install --no-cache-dir -r requirements_flask.txt

COPY . .

RUN mkdir -p uploads

EXPOSE 7860

ENV FLASK_ENV=production

CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "1", "--timeout", "120", "flask_app:app"]
