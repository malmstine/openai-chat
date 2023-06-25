FROM python:latest
RUN mkdir /app
COPY . /app/
WORKDIR /app
COPY ./requirements.txt /tmp/
RUN pip install -Ur /tmp/requirements.txt

COPY ./docker-entrypoint.sh /usr/bin/docker-entrypoint.sh
CMD ["bash", "/usr/bin/docker-entrypoint.sh"]