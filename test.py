#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import pytest
import json
import logging
import sys
import argparse

logger = logging.getLogger('speedtest-test')
from speedtest_influx import speedtest_handler , influxDBhandler , set_logging , main

#target = __import__("tplink_monitor.py")
#encrypt = target.encrypt



GOOD_IP = "192.168.1.134"
BAD_IP = "192.168.1.2"

#assume existance of docker-ised 
DB_HOST = "influxdb"
DB_PORT = "8086"
DB_USER = ""
DB_PASSWORD = ""
DB_DBNAME = "speedtest_db"


class Test_speedtest_handler(unittest.TestCase):
    def test_init(self):
        self.assertTrue(speedtest_handler())
       

    def test_grab_speed_test(self):
        sp = speedtest_handler();
        options = ["-f", "json"]
        self.assertTrue(sp.grab_speed_test(options))
        
    def test_format_speed_result(self):
        sp = speedtest_handler();
        item = "{'measurement': 'speedtest', 'tags_name':"
        json = {"measurement" : "speedtest",
                       "tags" : { 
                           "name" : "speedtest-test"
                           
                       
                       } } 
        result = sp.format_speed_result(json)
        logger.info(result)
        self.assertIn(item, str(result))
            
        


class TesttInfluxHandler(unittest.TestCase):
   
    def test_opendb(self):       
        influ = influxDBhandler(DB_HOST,DB_PORT,DB_USER,DB_PASSWORD,DB_DBNAME)
        influ.openDB(DB_HOST,DB_PORT,DB_USER,DB_PASSWORD,DB_DBNAME)
        self.assertTrue(influ)
        self.assertTrue(influ.db_close)
        
    def test_constructor(self):         
        influ = influxDBhandler(DB_HOST,DB_PORT,DB_USER,DB_PASSWORD,DB_DBNAME)
        self.assertTrue(influ)
        
    def test_create(self):         
        influ = influxDBhandler(DB_HOST,DB_PORT,DB_USER,DB_PASSWORD,DB_DBNAME)
        db = influ.create_db(DB_HOST,DB_PORT,DB_USER,DB_PASSWORD,DB_DBNAME)
        #print("DB = "+str(db))
        self.assertTrue(influ.db_close)
        self.assertTrue(db)    
        
        
    def test_bad_close(self):
        influ = influxDBhandler(DB_HOST,DB_PORT,DB_USER,DB_PASSWORD,DB_DBNAME)
        self.assertTrue(influ.db_close)   
    
    def test_write(self):         
        influ = influxDBhandler(DB_HOST,DB_PORT,DB_USER,DB_PASSWORD,DB_DBNAME)
        db = influ.create_db(DB_HOST,DB_PORT,DB_USER,DB_PASSWORD,DB_DBNAME)
        influ.openDB(DB_HOST,DB_PORT,DB_USER,DB_PASSWORD,DB_DBNAME)
        self.assertTrue(db)   
        json_body =  [{"measurement" : "speedtest",
                       "tags" : { 
                           "name" : "speedtest-test"
                           
                       
                       }, 
                       "fields" : {
                           "ping" : "12",
                           "test" : "True"
                       }}]
        db = influ.db_write(json_body)
        self.assertTrue(influ.db_close)
        self.assertTrue(db)         

class TesttMain(unittest.TestCase):
       
    def test_main(self):   
        
        self.assertTrue(main('--debug'))    
                
    def test_full_setup(self):   
        
        # opening part of the result... rest changes 
        item = "[{'measurement': 'speedtest', 'tags': {'name': 'speedtest'}, 'fields': {'type': 'result', 'timestamp':"
        #logger.info("Test full setup - Test open database")
        try:
         db = influxDBhandler(DB_HOST,DB_PORT,DB_USER,DB_PASSWORD,DB_DBNAME) 
         db.openDB(DB_HOST,DB_PORT,DB_USER,DB_PASSWORD,DB_DBNAME)
        except:
         logger.error("Test full setup -  Cannot open database") 
         quit("Cannot open database :" + str(DB_HOST)+str(DB_PORT)+str(DB_USER)+str(DB_PASSWORD)+str(DB_DBNAME))
        
        self.assertTrue(db)
        
        logger.info("Test full setup - Database open - test handler")
        try:
          speed =  speedtest_handler()
        except Exception as e:
            logger.error("Cannot start speed test")    
            quit("Cannot start speed test")
        try:
          options = ["-f", "json" , ]  
          result = speed.grab_speed_test(options)
        except Exception as e:
            logger.error("Cannot start speed test")    
            quit("Cannot start speed test")
              
        print("Speed test complete - test format result="+str(result))      
        #logger.info("Speed test complete - test format result="+str(result))
        db_res = speed.format_speed_result(result)
        #logger.info("Result for writing is:"+json.dumps(db_res,indent=2))
        self.assertIn(item,str(db_res))  
        self.assertTrue(db.db_write(db_res))
        self.assertTrue(db.db_close)          

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
    parser.add_argument('--speedtest', type=str, required=False, default='/speedtest',
                        help='Speetest script from Okallo')      
                       
    return parser.parse_args()      
                  
if __name__ == '__main__':
    
    
    args = parse_args()
    DB_HOST = args.host
    DB_PORT = args.port
    DB_USER = ""
    DB_PASSWORD = ""
    DB_DBNAME = "speedtest_db"
    
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    logger.info("Start test speedtest_influx test")
    set_logging(logger,True)
    unittest.main()