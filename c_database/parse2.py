import sys
import datetime
import psycopg2
from config import config

def insert_record(ts, ts_record, rtype, own_name, own_net, own_as, own_nc, hijack_name, hijack_as, link):
    """ insert a new vendor into the vendors table """
    sql = """INSERT INTO twitterfeed(ts, ts_record, rtype, own_name, own_net, own_as, own_nc, hijack_name, hijack_as, link)
             VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
    conn = None
    try:
        # read database configuration
        params = config()
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


inp = open("DATA3","r")

for l in inp:
    line = l.strip()
    #print(line)
    ts = "TS_NULL"
    ts_record = "REC_TS_NULL"
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

    line_c = line.split(",")
    line_d = line.split(",-,")

    if ( len(line_c) < 3 ):
        continue

    if ( len(line_d[1].split()) < 3 ):
        continue

    rtype = line_c[1]
    ts = datetime.datetime.now().isoformat()

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
        hijack_name = glueString(hn[0: len(hn)-2])
        # there can be junk around the hj AS# so we parse with some trepidation
        hijack_as_string = hn[0].split()[1]

        hijack_as = ""
        for n in hijack_as_string.replace("AS",""):
            if ( n.isdecimal() ):
                hijack_as = hijack_as + n
        hijack_as = int(hijack_as)
        link = line_c[len(line_c) - 1]

    insert_record(ts, ts_record, rtype, own_name, own_net, own_as, own_nc, hijack_name, hijack_as, link)
    #print( " >> ", str(ts)," | ",rtype," | ",own_name," | ",own_net," | ",own_as," | ",own_nc," | ",hijack_name," | ",hijack_as," | ",link)
    #print(" >> ----------------------------")
