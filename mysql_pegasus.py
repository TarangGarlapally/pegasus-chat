import mysql.connector
import random, datetime
import string
import random
import math
from dotenv import dotenv_values
import time


'''
mysql connection part
'''
env = dotenv_values(".env")

db = mysql.connector.connect(host = env["HOST"],
user = env["USER"],
password = env["PASSWORD"],
database = env["DATABASE"])



# cursor
cursor = db.cursor(buffered=True)

'''
mysql connection part end
'''





'''
DB queries
'''

def getMessages(name):
    cursor.execute("select * from messages where contact = '%s'"%name)
    messages = cursor.fetchall();
    return [{
    'time': message[1],
    'message': message[2],
    'Toxic':message[3],
    'Visible':message[4],
    'sent': True if message[5]=="sent" else False} for message in messages]



def insertMessage(content, mtype, contact, seen = True):
    timestamp = math.floor(time.time()*1000)
    uniqid = str(timestamp)+''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    val = (uniqid, timestamp, content, mtype, 1, contact)
    sql = """insert into messages (id, timestamp, content, type, seen, contact) values (%s, %s, %s, %s, %s, %s)"""
    cursor = db.cursor()
    cursor.execute(sql, val)
    db.commit()


def insertContact(contact, fname, lname):
    sql = """insert into contacts values(%s, %s, %s)"""
    val = (contact, fname, lname)
    cursor = db.cursor()
    cursor.execute(sql, val)
    db.commit()

def getContacts():
    cursor.execute("select * from contacts")
    return cursor.fetchall()

def isContact(contact):
    cursor.execute("select contact from contacts where contact = '{}'".format(contact))
    return cursor.fetchall()!=[]


'''
Below is the code for identifying the message based on it's
timestamp and reporting it.
'''

def reportToxic(messageTimeStamp):
    print(messageTimeStamp)
    pass

'''
Below is the code for identifying the message based on it's
timestamp and unreporting it.
'''

def reportNonToxic(messageTimeStamp):
    print(messageTimeStamp)
    pass

'''
Below is the code for viewing the message if user requested
'''

def viewMessage(messageTimeStamp):
    print(messageTimeStamp)
    sql = "UPDATE messages SET Visible = 1 WHERE timestamp = %s"
    cursor.execute(sql,(messageTimeStamp,))
    db.commit()

    print(cursor.rowcount, "record(s) affected")




'''
DB queries end
'''


