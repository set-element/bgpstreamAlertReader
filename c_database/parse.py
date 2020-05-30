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

    if ( len(line_c) < 3 ):
        continue

    rtype = line_c[1]
    ts = datetime.datetime.now().isoformat()

    if ( rtype == "OT" ):
        # BGP,OT,264491,Orsine e Souza Telecomunica��es LTDA,-,Outage affected 24 prefixes, https://t.co/i3MLk7se3J
        # if len(line_c) == 7 we can just parse this like civilized humans
        if ( len(line_c) == 7 ):
            own_name = line_c[3]
            own_as = line_c[2]
            own_nc = int( line_c[5].split()[2] )
            link = line_c[6]
        else:
            print(" >> SKIP OT")

    if ( rtype == "HJ" ):
            # BGP,HJ,hijacked prefix AS24961 177.73.156.0/22, myLoc managed IT AG,-,By AS18479 Universo Online S.A., https://t.co/sSwyGK9cE7
        if ( len(line_c) == 7 ):
            own_name = line_c[3]
            own_net = line_c[2].split()[3]
            own_as = int(line_c[2].split()[2].replace("AS",""))
            hijack_name = line_c[5]
            hijack_as = int(line_c[5].split()[1].replace("AS",""))
            link = line_c[6]
        else:
            # BGP,HJ,hijacked prefix AS8308 193.59.93.0/24, Naukowa I Akademicka Siec Komputerowa Instytut Badawczy,-,By AS42624… https://t.co/QDej82OmD8
            # BGP,HJ,hijacked prefix AS8100 170.231.236.0/24, QuadraNet, Inc,-,By AS42624 Simple Carrier LLC, https://t.co/QBYZhZ1rC5
            print(" ALT HJ")
            own_name = line_c[3] + line_c[4]
            own_net = line_c[2].split()[3]
            own_as = int(line_c[2].split()[2].replace("AS",""))
            tmp_hijack_name = line.split(",-,")[1].split()
            # this is super unclean, but there can be junk on the end of the AS numeric if the message
            #   has run out of space
            hijack_as = ""
            for n in tmp_hijack_name[1].replace("AS",""):
                if ( n.isdecimal() ):
                    hijack_as = hijack_as + n
            hijack_name = line.split(",-,")[1].split(", https")[0]
            hijack_as = int(hijack_as)
            link = tmp_hijack_name[ len(tmp_hijack_name) -1 ]


    #insert_record(ts, ts_record, rtype, own_name, own_net, own_as, own_nc, hijack_name, hijack_as, link)
    print( " >> ", str(ts)," | ",rtype," | ",own_name," | ",own_net," | ",own_as," | ",own_nc," | ",hijack_name," | ",hijack_as," | ",link)
    #print(" >> ----------------------------")
