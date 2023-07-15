FROM python:alpine3.8

RUN pip install pipenv
COPY Pipfile* ./
RUN pipenv install --system

COPY src ./src

EXPOSE 8000
CMD uvicorn api.main:api --app-dir src --host 0.0.0.0