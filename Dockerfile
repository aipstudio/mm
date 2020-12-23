FROM python:3-slim

WORKDIR /usr/src/app

RUN pip install --no-cache-dir flask requests

COPY . .

CMD [ "python", "./mm.py" ]
