FROM python:3.11-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY requirement.txt .
RUN pip install -r requirement.txt

COPY . .

# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "shop.wsgi:application"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]