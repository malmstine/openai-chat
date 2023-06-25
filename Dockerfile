FROM python:latest
RUN mkdir /app
COPY ./docker-entrypoint.sh /usr/bin/docker-entrypoint.sh
COPY . /app/
WORKDIR /app
COPY ./requirements.txt /tmp/
RUN pip install -Ur /tmp/requirements.txt

CMD ["bash", "/usr/bin/docker-entrypoint.sh"]