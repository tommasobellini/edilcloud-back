FROM python:3.5
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN mkdir /office2017.whistle.it
WORKDIR /office2017.whistle.it
COPY requirements.txt /office2017.whistle.it/
RUN apt-get install gcc
RUN pip install psycopg2
# Install Gunicorn.
RUN pip install "gunicorn>=19.8,<19.9"
RUN pip install -r requirements.txt
COPY . /office2017.whistle.it/
RUN cd /var/log/ && mkdir django && touch whistle-api_exceptions.log

EXPOSE 80

CMD python manage.py runserver 0.0.0.0:80
