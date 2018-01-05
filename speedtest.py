#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from datetime import date, datetime, timedelta
#import mysql.connector
import MySQLdb
import time
#from mysql.connector import errorcode

import subprocess

try:
    # for Python 2.x
    from StringIO import StringIO
except ImportError:
    # for Python 3.x
    from io import StringIO
import csv

config = {
  'user': 'speed',
  'passwd': 'tiger',
  'host': '192.168.1.1',
  'db': 'speedlog'
}

print('running Database')
cnx = MySQLdb.connect(**config)
  



print('running speedtest')
speed = subprocess.check_output(["./speedtest-cli","--csv"])
print (speed)
f = StringIO(speed)
reader = csv.reader(f, delimiter=',')
for row in reader:
      dummy = 1

speeddate = row[3]
pingtime = row[5]
downspeed = float( row[6]) / 1000000
upspeed = float (row[7]) / 1000000
print(speeddate,pingtime,downspeed,upspeed)

cursor = cnx.cursor()
cur_time = time.time()
datetimeWrite = datetime.fromtimestamp(cur_time).strftime('%Y-%m-%d %H:%M:%S')
sql = ("""INSERT INTO speed (Date,ping,down,up) VALUES (%s,%s,%s,%s)""",(datetimeWrite,pingtime,downspeed,upspeed))
try:
   # Execute the SQL command
   cursor.execute(*sql)
   # Commit your changes in the database
   cnx.commit()
except:
   # Rollback in case there is any error
   cnx.rollback()
   print ('fred')
   print (cnx.error)
   print ("Failed writing to database", sql)
finally:
    cnx.close()
