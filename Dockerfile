FROM python:3.10-alpine
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt && mkdir /status_bot
COPY ./code /app
COPY ./server-icons /status_bot
ENV BOT_ID=""
ENTRYPOINT [ "python" ]
CMD [ "status_bot.py" ]