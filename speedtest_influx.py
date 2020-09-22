#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
from datetime import date, datetime, timedelta
#import mysql.connector
import time, sys
#from mysql.connector import errorcode
import logging.handlers
import logging
import subprocess
import argparse
import struct
from threading import Timer
import socket
import json
from flatten_json import flatten
import os.path
#from typing import Any, Dict, Union
#try:
from influxdb import InfluxDBClient
#except:
#   print("no influxdb client installed")
#   quit("no influx")

try:
       from io import StringIO
except:
       print("Cannot import io")       
import csv

''' argsig = {
  'user': 'speed',
  'passwd': 'tiger',
  'host': '192.168.1.27',
  'db': 'Stats'
} '''

#PROG = ["/speedtest"]
PROG = ["/usr/local/bin/speedtest"]
OPTIONS = ["-f",  "json"]
SERVERS = [ "35422" , "35026" , "3448" , "24384"]
PROG_CLI = ["/speedtest"]
#PROG_CLI = ["/usr/local/bin/speedtest"]
OPTIONS_CLI = [""]
#OPTIONS = "--csv"

logger = logging.getLogger('speedtest')

class speedtest_cli_handler():
    
    def __init__(self):
       if (not os.path.exists(str(''.join(PROG_CLI)))):  
         logger.error("No "+ str(PROG_CLI)+ " program available")
         #raise("No  python speedtest program avaialble")
    
        
    def grab_speed_test(self):
        
        
        logger.info('running speedtest')
        speed = subprocess.check_output(PROG_CLI+OPTIONS_CLI)
        logger.info(speed)
        return speed
        f  = StringIO(speed)
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            dummy = 1
        return row
        
        
    
    
    def format_speed_result(self,row):
        speeddate = row[3]
        pingtime = row[5]
        downspeed = float( row[6]) / 1000000
        upspeed = float (row[7]) / 1000000
        print(speeddate,pingtime,downspeed,upspeed)    
        
        json_body = [{ "measurement" : "speedtest",
                       "tags" : { 
                           "name" : "speedtest"
                           
                       
                       },
                       "fields" : {
                           "date" : speeddate,
                           "ping" : pingtime,
                           "download" : downspeed,
                           "upload" : upspeed
                       }
        }]
                     
                     
        logger.debug("Completed Value for writting :{0}".format(json_body))               
        return json_body    
    
class speedtest_handler():
    
    
    def __init__(self,prog):
        
        if (not os.path.exists(str(''.join(prog)))):  
         logger.error("No "+ str(prog)+ " program available")
         quit("No Ookla speedtest program avaialble:"+str(prog))
        self.prog = prog
        
    def grab_speed_test(self,options):
        
        
        logger.debug('running speedtest')
        speed = json.loads(subprocess.check_output(self.prog+options))
        logger.debug("Speed run raw result:!!"+str(speed)+"!!")
        return speed
   
        
    
    
    def format_speed_result(self,row):
        #speeddate = row[3]
        #pingtime = row[5]
        #downspeed = float( row[6]) / 1000000
        #upspeed = float (row[7]) / 1000000
        #print(speeddate,pingtime,downspeed,upspeed)    
        items = flatten(row)
        json_body = [{ "measurement" : "speedtest",
                       "tags" : { 
                           "name" : "speedtest"
                           
                       
                       },
        #               "fields" : {
        #                   "date" : speeddate,
        #                   "ping" : pingtime,
        #                   "download" : downspeed,
        #                   "upload" : upspeed
                       "fields" : items 
                       }
        ]
                     
        logger.debug("Completed Value for writting :{0}".format(json_body))               
        return json_body    
    
class influxDBhandler():
    def __init__(self,host,port,user,password,dbname):
        dummy = []
        #try:
        #    self.connection = self.openDB(host,port,user,password,dbname)
        #except Exception as err:
        #    logger.error(err)
        #    raise ValueError("Could not open db on object init {0}".format(err) )
                

    def openDB(self,host,port,user,password,dbname):
        """Needs error hanlding etc"""
        #logger.debug("openning db {0} on host {1}".format(dbname,host))
        try: 
            client = InfluxDBClient(host, port, user, password, dbname)
        except Exception as e:
            print("didnt open db")    
            logger.error("Didn't open db:"+str(e))
            return False    
        
        try:
            dbs = client.get_list_database()
            logger.debug ("DBS available: {0}".format(dbs))
            client.switch_database(dbname)
            client.switch_user(user, password )
            dbs = client.get_list_measurements()
            logger.debug ("DB opened: {0}".format(dbs))
        except Exception as e:
            print("didnt change db")    
            logger.error("Didn't change open db:"+str(e))
            return False 
            
        self.db = client
        return True

    def create_db(self,host, port, user, password, dbname):
        client = InfluxDBClient(host, port, user, password, dbname)
        logger.debug("self ="+str(self))
        try:
            client.drop_database(dbname)
        except Exception as e:
            print("didnt drop old db")    
            logger.error("Didn't drop old db:"+str(e))
            return False
        try:
             client.create_database(dbname)
        except Exception as e:
            print("db not created - {0}".format(e))
            return False
        except:
            print("unknown error openning db") 
            return False    
        print("db created")
        try:
             client.create_retention_policy('infinite retention', 'INF', 3, default=True)
        except Exception as e:
            print("retention policy not set - {0}".format(e))
            logger.error("retention policy not set - {0}".format(e))
            return False
        except:
            print("unknown error openning db") 
            return False  
        client.close() 
        return True 
    
    
    def db_write(self,value):
        """ Fix the data and write to influx db"""   
        logger.debug("items to write - {0}".format(value))  
        #print(self.db)
        try:     
            
            self.db.write_points(value) #,protocol=u'json')  
            logger.debug("Data written to Influx db: {0}".format(value))    
        except Exception as e:
            logger.error("db not written - {0} for {1}".format(e,json.dumps(value)))
            return False
        return True
        
    def db_close(self):
        try:
            self.db.close()
        except Exception as e:
            logger.error("db not closed - {0}".format(e))
            return False        


def Usage():
    #     print __doc__
      print ("Speedtest - capture internet speed to influxdb")

def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='Captures internet speed to influxdb.')
    parser.add_argument('--host', type=str, required=False,
                        default='localhost',
                        help='hostname of InfluxDB http API')
    parser.add_argument('--port', type=int, required=False, default=8086,
                        help='port of InfluxDB http API')
    parser.add_argument('--database', type=str, required=False, default='speedtest_db',
                        help='Database name on influxDB')
    parser.add_argument('--user', type=str, required=False, default='',
                        help='User for influxDB')
    parser.add_argument('--password', type=str, required=False, default='',
                        help='Password for influxDB')
    parser.add_argument('--create_db', type=bool, required=False, default=False,
                        help='Create the db')    
    parser.add_argument('--debug', action='store_true',   help='print debug messages to stderr')
    parser.add_argument('--speedtest-cli', type=str, required=False, default='/speedtest-cli',
                        help='Speedtest cli location')  
    parser.add_argument('--speedtest', type=str, required=False, default='/usr/local/bin/speedtest',
                        help='Speetest script from Okallo')      
    parser.add_argument('--loop', action='store_true',   help='loop') 
    parser.add_argument('--loop-delay', type=int, required=False, default=900,
                        help='loop sleep time')                    
    return parser.parse_args()      

def set_logging(logger, debug):
     
    #logging.basicargsig(format='%(asctime)s: %(message)s', level=logging.INFO)
    ch = logging.handlers.RotatingFileHandler(
        "speedtest.log", mode='a', maxBytes=100000, backupCount=5, encoding=None, delay=0)
    #ch = logging.StreamHandler()
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)    

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    
def main(args_passed):
    print("Start speedtest args"+str(args_passed))
    logger.debug("start speedtest"+str(args_passed))
    args = parse_args()
    
    PROG = [args.speedtest]
    #print("speedtest = "+str(PROG))
    set_logging(logger,args.debug)
    DataJSON = {}
    
    """ Open mysql connection """
    logger.debug("open database")
    try:
        db = influxDBhandler(args.host,args.port,args.user,args.password,args.database) 
        db.openDB(args.host,args.port,args.user,args.password,args.database)
    except:
        logger.error("Cannot open database") 
        quit("Cannot open database :" + str(args.host)+str(args.port)+str(args.user)+str(args.password)+str(args.database))
        return False   
     
    logger.debug("Run speedtest") 
    try:
        speed =  speedtest_handler(PROG)
    except Exception as e:
        logger.error("Cannot start speed test")    
        quit("Cannot start speed test")
    
    options = OPTIONS
    result = speed.grab_speed_test(options)
    logger.debug("Speedtest complete - test format result="+str(result))
    db_res = speed.format_speed_result(result)
    
    db.db_write(db_res)
    logger.info("Successful write to DB")
    
    db.db_close()
    
    return True
    


if __name__ == '__main__':
    
    
    main(sys.argv[1:])             
   
        
    


