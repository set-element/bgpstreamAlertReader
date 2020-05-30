#!/usr/bin/python
 
import psycopg2
from config import config
 
 
def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE twitterfeed (
            ts VARCHAR(32),
            ts_record VARCHAR(32),
            rtype VARCHAR(8),
            own_name VARCHAR(128),
            own_net VARCHAR(32),
            own_as INT,
            own_nc INT,
            hijack_name VARCHAR(128),       
            hijack_as  INT,
            link VARCHAR(64)
        )
        """
       , )
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            print("RUNNING: ", command)
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
 
 
if __name__ == '__main__':
    create_tables()
