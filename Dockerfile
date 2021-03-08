FROM python:3

# Install everything
RUN apt-get -qq update && apt-get -qq install sqlite3 cron -y

# Cron setup
RUN touch /var/log/cron.log
COPY crontab /etc/cron.d/rkpop_youtube
RUN chmod 0644 /etc/cron.d/rkpop_youtube

# Applicaiton setup
RUN mkdir /var/youtube
WORKDIR /var/youtube

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ENV setup
ARG DB_PATH
ARG HEADERS_PATH
# We need to do this to make the environment variables available in cron
RUN env >> /etc/environment

# DB setup
RUN mkdir -p $(dirname $DB_PATH)
RUN touch $DB_PATH
RUN sqlite3 $DB_PATH < ./youtube.db.schema

# Run
CMD [ "cron", "-f" ]
