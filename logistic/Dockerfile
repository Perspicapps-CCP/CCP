FROM python:3.13
WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system --deploy


COPY . .


RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser
