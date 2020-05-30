#!/usr/bin/env python

#-----------------------------------------------------------------------
# twitter-stream-format:
#  real-time stream of twitter's public timeline.
#-----------------------------------------------------------------------

from twitter import *
import datetime
import os
from time import strftime
from email.utils import parsedate

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

    # Parse the raw text into "," bits
    # Each hijacked netblock gets it's own message which is nice
    t_text_p = t_text.split(",")
    nttp = len(t_text_p)

    if ( len(t_text_p) < 7 ):
            continue

    verb = t_text_p[1]         # 'HJ'


    if (verb == "HJ"):

        skip = 0
        stolen = t_text_p[2]       # 'hijacked prefix AS39120 185.104.125.248/32'
        AS = t_text.split(",By AS")[1].split()[0]
        realtime = datetime.datetime.now().isoformat()

        # Extract the prefix - should always be the last string
        stolen_c = stolen.split()
        netblock = stolen_c[len(stolen_c)-1]

        # If the AS can't be expressed as an int there is something
        #  really weird going on and we move along ....
        try:
            int(AS)
        except ValueError:
            skip = 1

        if ( skip == 0 ):
            logentry = realtime + "," + timetext + "," + AS + "," + netblock + "\n"
            logfile.write(logentry)
            # for the inpatient humans in the crowd
            print(realtime,timetext,AS,netblock)
