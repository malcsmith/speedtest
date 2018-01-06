#!/bin/bash

echo "putting speedtest into cron"
/usr/bin/crontab /etc/cron.d/speedtest-cron

echo "initial run of speedtest on startup"
cd /
/speedtest.py

echo "starting cron"
cron -f 