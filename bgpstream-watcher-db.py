#!/usr/bin/env python

#-----------------------------------------------------------------------
# twitter-stream-format:
#  real-time stream of twitter's public timeline.
#-----------------------------------------------------------------------

from twitter import *
import datetime
import os
from time import strftime
from time import sleep
from email.utils import parsedate
import sys
import psycopg2


#-----------------------------------------------------------------------
# mod path for database code
#-----------------------------------------------------------------------
sys.path.append("/home/scottc/development/bgpstreamtwitterbot")
import c_database.config

#-----------------------------------------------------------------------
# load our API credentials
#-----------------------------------------------------------------------

try:
    consumer_key = os.environ['CONSUMER_KEY']
except KeyError as e:
    print(e)
    print("Set CONSUMER_KEY environment variable")
    exit()

try:
    consumer_secret = os.environ['CONSUMER_SECRET']
except KeyError as e:
    print(e)
    print("Set CONSUMER_SECRET environment variable")
    exit()

try:
    access_key = os.environ['ACCESS_KEY']
except KeyError as e:
    print(e)
    print("Set ACCESS_KEY environment variable")
    exit()

try:
    access_secret = os.environ['ACCESS_SECRET']
except KeyError as e:
    print(e)
    print("Set ACCESS_SECRET environment variable")
    exit()

def insert_record(ts, ts_record, rtype, own_name, own_net, own_as, own_nc, hijack_name, hijack_as, link):
    """ insert a new vendor into the vendors table """
    sql = """INSERT INTO twitterfeed(ts, ts_record, rtype, own_name, own_net, own_as, own_nc, hijack_name, hijack_as, link)
             VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
    conn = None
    try:
        # read database configuration
        params = c_database.config.config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (ts, ts_record, rtype, own_name, own_net, own_as, own_nc, hijack_name, hijack_as, link))
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def glueString(items):
    ret_val = ""

    for s in items:
        ret_val = ret_val + " " + s

    return ret_val

def parseTwitterLine(ts_record, line):

    # default data values
    ts = "TS_NULL"
    rtype = "RTNULL"
    # owner
    own_name = "OWN_NAME"
    own_net = "OWN_NET"
    own_as = 0
    own_nc = 0
    # hijacker, if appropriate
    hijack_name = "HIJ_NAME"
    hijack_as = 0
    #
    link = "LINK"

    # these are the default strings that will be parsed
    line_c = line.split(",")
    line_d = line.split(",-,")

    # not everything we see is clean and well behaved - drop
    #   out if things seem to be too weird
    if ( len(line_c) < 3 ):
        return

    if ( len(line_d[1].split()) < 3 ):
        return

    rtype = line_c[1]
    ts = datetime.datetime.now().isoformat()

    # parse based on record type
    if ( rtype == "OT" ):
        # BGP,OT,264491,Orsine e Souza Telecomunica��es LTDA,-,Outage affected 24 prefixes, https://t.co/i3MLk7se3J
        own_name = glueString( line_d[0].split(",")[3:] )

        # this is not always a number (ex country code etc),  only set if
        #   there is something here
        if ( line_c[2].isnumeric() ):
            own_as = line_c[2]

        own_nc = int( line_d[1].split()[2] )
        link = line_c[len(line_c) - 1]

    if ( rtype == "HJ" ):
        # BGP,HJ,hijacked prefix AS24961 177.73.156.0/22, myLoc managed IT AG,-,By AS18479 Universo Online S.A., https://t.co/sSwyGK9cE7
        own_name = glueString( line_d[0].split(",")[3:] )
        own_net = line_c[2].split()[3]
        own_as = int(line_c[2].split()[2].replace("AS",""))
        #
        hn = line_d[1].split(",")
        hijack_name = glueString(hn[0: len(hn)-1])
        # there can be junk around the hj AS# so we parse with some trepidation
        hijack_as_string = hn[0].split()[1]

        hijack_as = ""
        for n in hijack_as_string.replace("AS",""):
            if ( n.isdecimal() ):
                hijack_as = hijack_as + n
        hijack_as = int(hijack_as)
        link = line_c[len(line_c) - 1]

    # insert record into database
    insert_record(ts, ts_record, rtype, own_name, own_net, own_as, own_nc, hijack_name, hijack_as, link)
    print( " >> ", str(ts)," | ",rtype," | ",own_name," | ",own_net," | ",own_as," | ",own_nc," | ",hijack_name," | ",hijack_as," | ",link)

#-----------------------------------------------------------------------
# create/open logfile
#-----------------------------------------------------------------------
logfile = open("LOGFILE", "a")


#-----------------------------------------------------------------------
# create twitter streaming API object
#-----------------------------------------------------------------------
auth = OAuth(access_key,
             access_secret,
             consumer_key,
             consumer_secret)
stream = TwitterStream(auth = auth, secure = True)

#-----------------------------------------------------------------------
# iterate over tweets matching this filter text
#-----------------------------------------------------------------------

# Put this into a while True loop cause the connection times out
#   on occasion

while True:

    # bgpstream Twitter Numeric ID: 3237083798
    # bgpmon Twitter Numeric ID: 156304292
    tweet_iter = stream.statuses.filter(follow="3237083798")

    for tweet in tweet_iter:

        # turn the date string into a date object that python can handle
        try:
            ca_date = tweet["created_at"]
        except KeyError as e:
            print(e)
            continue

        timestamp = parsedate(ca_date)

        # now format this nicely into HH:MM:SS format
        timetext = strftime("%H:%M:%S", timestamp)

        try:
            t_text = tweet["text"]
        except KeyError as e:
            print(e)
            continue

        # convert the newline into a space cause human communication
        t_text = t_text.replace("\n"," ")

        # This is mostly for debug
        print(t_text)

        # Makes parsing simple above to do this
        parseTwitterLine(timetext, t_text)

    sleep(10)
