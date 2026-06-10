FROM python:3.14-slim
WORKDIR /code
# python dependencies
RUN pip install pipenv
COPY Pipfile .
COPY . .
RUN pipenv install --skip-lock
ENTRYPOINT ["pipenv", "run", "python", "main.py"]