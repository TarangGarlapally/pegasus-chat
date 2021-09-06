import mysql.connector
import random, datetime
import string
import random
import math
from dotenv import dotenv_values
import time

from oauth2client.crypt import _verify_signature
from requests.adapters import SSLError

'''
mysql connection part
'''
env = dotenv_values(".env")

db = mysql.connector.connect(host = env["HOST"],
user = env["USER"],
password = env["PASSWORD"],
database = env["DATABASE"], ssl_ca = env["SSL_CA"], ssl_cert = env["SSL_CERT"], ssl_key = env["SSL_KEY"])



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
    'sent': True if message[3]=="sent" else False} for message in messages]



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
DB queries end
'''


