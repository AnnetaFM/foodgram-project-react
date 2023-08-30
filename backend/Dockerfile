FROM python:3.9

WORKDIR /foodgram

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir 
COPY . .

# При старте контейнера запустить сервер разработки.
CMD ["python", "manage.py", "runserver", "0:8000"] 