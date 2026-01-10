FROM python:3.14-rc-slim-bookworm

WORKDIR /app

COPY requirements/base.txt ./

RUN pip install -r base.txt

COPY markovbot ./markovbot
COPY bot.py ./

CMD [ "python", "bot.py" ]
