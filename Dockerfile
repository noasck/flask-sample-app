# pull official base image
FROM python:3.11.3-slim-buster

# set work directory
WORKDIR /usr

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./src/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# copy project
COPY ./src /usr/src
RUN chmod u+x /usr/src/entrypoint.sh

ENTRYPOINT [ "/usr/src/entrypoint.sh" ]
