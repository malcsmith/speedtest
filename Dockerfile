FROM alpine:latest
MAINTAINER Malcolm Smith

# Install Supporting Packages
RUN apk --no-cache  -q update && \
  apk add --no-cache bash curl python wget  \
  py-mysqldb python-dev mysql-client py-pip tini 

#  RUN pip install -U pip && pip install MySQL-python
  RUN  pip install MySQL-python

# Grab the fresh version of speedtest
  RUN wget -O /speedtest-cli https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py
  RUN chmod a+x /speedtest-cli

#copy and prep speedtest
  COPY speedtest.py /speedtest.py
  RUN chmod a+x /speedtest.py


# Add crontab file in the cron directory
ADD crontab /etc/cron.d/speedtest-cron
 
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/speedtest-cron
 
# Create the log file to be able to run tail
RUN touch /var/log/speedtest.log

RUN crontab -l | { cat; echo "1,16,31,46 * * * *  /speedtest.py " ; echo "* * * * *           echo test" ; } | crontab -
 
# Run the command on container startup
CMD ["/usr/sbin/crond", "-f"]
