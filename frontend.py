from PyQt5 import QtWidgets,uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QLineEdit,QMainWindow,QPushButton, QScrollArea, QWidget, QVBoxLayout
import sys,time
import image_rc, add_rc
import mysql.connector
import time
import random
import string
import math
from dotenv import dotenv_values

'''
mysql connection part
'''

env = dotenv_values(".env")


db = mysql.connector.connect(host = env["HOST"],
user = env["USER"],
password = env["PASSWORD"],
database = env["DATABASE"]);

# cursor
cursor = db.cursor()

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
    'recieved': True if message[3]=="recieved" else False} for message in messages]



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


'''
DB queries end
'''





'''
global functions
'''

def own_date_label(text):
    label=QLabel(text)
    label.setStyleSheet("color:white;\nfont: 87 8pt Arial Black")
    label.setAlignment(Qt.AlignCenter)
    return label

def own_message_label(text,sent):
    label=QLabel(text)
    label.setStyleSheet("background-color:#333399;color:#fff;font-size:20px;margin:15px 0px 15px 0px;padding:5px 0px 5px 0px;border:0px solid transparent;border-radius:5px")
    if sent:
        label.setAlignment(Qt.AlignRight)
    else:
        label.setAlignment(Qt.AlignLeft)
    return label

def own_push_button(text):
    button=QPushButton(text)
    button.setObjectName(text.replace(' ',''))
    button.setStyleSheet("background-color:#333399;color:#fff;font-size:20px;margin:15px 0px 15px 0px;padding:5px 0px 5px 0px;border:0px solid transparent;border-radius:5px")
    return button


class add(QWidget):
    def __init__(self):
        super(add,self).__init__()

        uic.loadUi('addcontact.ui',self)
    
    def display(self,chatWindow):
        self.show()

        '''
        logic for adding contact
        '''



        '''
        returning to chatWindow
        '''
        self.findChild(QPushButton,"addcontactButton").clicked.connect(lambda state,chatWindow=chatWindow: self.next(chatWindow))
    
    def next(self,chatWindow):
        self.close()




class Chat(QMainWindow):
    def __init__(self):
        super(Chat,self).__init__()

        '''
        Loading the chatWindow UI
        '''
        uic.loadUi('chat.ui',self)
        

        '''
        Below List contains all the contacts of the user(needs to be added dynamically) and their buttons need to be stored in the class
        '''

        # Reading contacts
        cursor.execute("select * from contacts")
        contacts = cursor.fetchall()

        self.contacts=contacts
        self.contactsList=self.findChild(QVBoxLayout,"contactsList")
        for contact in self.contacts:
            self.contactsList.addWidget(own_push_button(contact[0]))
        self.contactButtons=[]
        for contact in self.contacts:
            name=contact[0]
            self.contactButtons.append(self.findChild(QPushButton,name))
        

        
        '''
        Adding previous messages(for now dummy)
        '''
        self.gridlayout=self.findChild(QGridLayout,"chatLayout")
        for i in range(3):
            self.gridlayout.setColumnStretch(i,1)
        for i in range(11):
            self.gridlayout.setRowStretch(i,1)
        self.i=0
        
        # scrollArea=self.findChild(QScrollArea,"chatArea")
        # scrollArea.setWidget(gridlayout)
        # scrollArea.setWidgetResizable(True)
        


        '''
        Below is the code for selecting send button and calling the resp. function
        '''
        self.sendButton=self.findChild(QPushButton,"sendButton")
        self.sendButton.clicked.connect(self.send)
        addWindow=add()
        self.findChild(QPushButton,"addButton").clicked.connect(lambda state,addWindow=addWindow: self.add(addWindow))

        '''
        Below is the code for updating messageSection based on the contact selected
        '''
        mapping=[]
        for i in range(0,len(self.contacts)):
            mapping.append((self.contactButtons[i],self.contacts[i][0]))
        for button,name in mapping:
            button.clicked.connect(lambda state,name=name: self.messageSection(name))

            
    
        
    
    def messageSection(self,name):
        self.findChild(QLabel,"headName").setText(name)
        messages=getMessages(name)
        for i in reversed(range(self.gridlayout.count())): 
            self.gridlayout.itemAt(i).widget().setParent(None)
        self.i=0
        if len(messages)!=0:
            self.gridlayout.addWidget(own_date_label(messages[0]['time']),0,1)
            self.i += 1
            for message in messages:
                self.gridlayout.addWidget(own_message_label(message["message"], False),self.i, 0 if message["recieved"] else 2)
                self.i += 1
                
        

    def send(self):
        inputField=self.findChild(QLineEdit,"message")
        message=inputField.text()
        newLabel=own_message_label(message,False)
        inputField.clear()

        gridlayout=self.findChild(QGridLayout,"chatLayout")

        gridlayout.addWidget(newLabel,self.i,2)

        self.i += 1
        insertMessage(message, "sent", self.findChild(QLabel,"headName").text(), True)







        
    
    def add(self,addWindow):
        addWindow.display(self)


    def display(self):
        self.show()


class welcome(QMainWindow):
    def __init__(self):
        super(welcome,self).__init__()

        uic.loadUi('Welcome.ui',self)
    def display(self):
        self.show()
        '''
        Need to add logging code below
        '''


        '''
        button press event
        '''
        chatWindow=Chat()
        self.findChild(QPushButton,"loginButton").clicked.connect(lambda state,chatWindow=chatWindow: self.next(chatWindow))
    
    def next(self,chatWindow):
        self.close()
        chatWindow.display()
    





def display():
    app=QApplication(sys.argv)
    welcomeWindow=welcome()
    welcomeWindow.display()
    app.exec_()

if __name__ == "__main__":
    display()
