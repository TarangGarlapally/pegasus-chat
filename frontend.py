from PyQt5 import QtWidgets,uic
from PyQt5.QtCore import Qt, fixed
from PyQt5.QtWidgets import QApplication, QGridLayout, QHBoxLayout, QLabel, QLineEdit,QMainWindow,QPushButton, QScrollArea, QSpacerItem ,QSizePolicy, QWidget, QVBoxLayout
import sys,time
import image_rc, add_rc
import mysql.connector
import time
import random, datetime
import string
import math
from dotenv import dotenv_values
import firebase


'''
Firebase part
'''
firebase = firebase.init()
auth = firebase.auth()
user = "none"
'''
Firebase part end
'''

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


'''
DB queries end
'''





'''
global functions
'''

def showAlert(message, description, title):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information if message=="Information" else QtWidgets.QMessageBox.Critical)
    msg.setText(message)
    msg.setInformativeText(description)
    msg.setWindowTitle(title)
    msg.exec_()

def own_date_label(text):
    week_days=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    date=datetime.datetime.fromtimestamp(float(text)//1000.0)
    time_o=""+str(date.day)+" "+week_days[date.month-1]+" "+str(date.year)+" "+str(date.time())
    hbox=QHBoxLayout()
    label=QLabel(time_o)
    label.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
    label.setMinimumWidth(70)
    label.setMinimumHeight(20)
    label.setStyleSheet("color:white;\nfont: 87 8pt Arial Black")
    label.setAlignment(Qt.AlignCenter)
    hbox.addWidget(label)
    return hbox
def own_message_label(text,sent):
    hbox=QHBoxLayout()
    label=QLabel(text)
    label.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
    label.setMaximumWidth(450)
    label.setMinimumHeight(60)
    label.setWordWrap(True)
    label.setStyleSheet("background-color:#333399;color:#fff;font-size:20px;margin:15px 0px 15px 0px;padding:5px;border:0px solid transparent;border-radius:5px")
    if sent:
        label.setAlignment(Qt.AlignRight)
        hbox.addStretch(1)
        hbox.addWidget(label)
    else:
        label.setAlignment(Qt.AlignLeft)
        hbox.addWidget(label)
        hbox.addStretch(1)
    return hbox

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
        self.vlayout=self.findChild(QVBoxLayout,"chatLayout")
        self.vlayout.setAlignment(Qt.AlignTop)

        self.scrollArea=self.findChild(QScrollArea,"scrollArea")
        scroll_bar = self.scrollArea.verticalScrollBar()
        scroll_bar.rangeChanged.connect(lambda: scroll_bar.setValue(scroll_bar.maximum()))
                


        '''
        Below is the code for selecting send button and calling the resp. function
        '''
        self.sendButton=self.findChild(QPushButton,"sendButton")
        self.sendButton.clicked.connect(self.send)
        inputField=self.findChild(QLineEdit,"message")
        inputField.returnPressed.connect(self.send)
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
        def deleteItems(layout):
             if layout is not None:
                 while layout.count():
                     item = layout.takeAt(0)
                     widget = item.widget()
                     if widget is not None:
                         widget.deleteLater()
                     else:
                         deleteItems(item.layout())
        deleteItems(self.vlayout)
        
        messages=getMessages(name)
        if len(messages)!=0:
            for message in messages:
                self.vlayout.addLayout(own_date_label(message['time']))
                self.vlayout.addLayout(own_message_label(message["message"],message["sent"]))
        
    
    def send(self):
        inputField=self.findChild(QLineEdit,"message")
        message=inputField.text()
        if message!="":
            newMessageLayout=own_message_label(message,True)
            timestamp = math.floor(time.time()*1000)
            inputField.clear()
            self.vlayout.addLayout(own_date_label(timestamp))
            self.vlayout.addLayout(newMessageLayout)
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
        self.findChild(QPushButton,"loginButton").clicked.connect(lambda state, chatWindow=chatWindow: self.next("login", chatWindow))
        self.findChild(QPushButton,"singupButton").clicked.connect(lambda state, chatWindow=chatWindow: self.next("signup", chatWindow))
        self.findChild(QLineEdit,"username").returnPressed.connect(lambda chatWindow=chatWindow: self.next("login", chatWindow))
        self.findChild(QLineEdit,"password").returnPressed.connect(lambda chatWindow=chatWindow: self.next("login", chatWindow))
        self.findChild(QLineEdit,"fname").returnPressed.connect(lambda chatWindow=chatWindow: self.next("signup", chatWindow))
        self.findChild(QLineEdit,"lname").returnPressed.connect(lambda chatWindow=chatWindow: self.next("signup", chatWindow))
        self.findChild(QLineEdit,"email").returnPressed.connect(lambda chatWindow=chatWindow: self.next("signup", chatWindow))
        self.findChild(QLineEdit,"password_2").returnPressed.connect(lambda chatWindow=chatWindow: self.next("signup", chatWindow))
        self.findChild(QLineEdit,"reenter").returnPressed.connect(lambda chatWindow=chatWindow: self.next("signup", chatWindow))
    
    def next(self,type,chatWindow):
        if(type == "login"):
            email = self.findChild(QLineEdit,"username").text()
            password = self.findChild(QLineEdit,"password").text()
            if(email == "" or password == ""):
                showAlert('Incomplete details', 'Please fill all the fields', 'Error')
                return
            try:
                global user
                user = auth.sign_in_with_email_and_password(email, password)
                print(user)
                verified = auth.get_account_info(user['idToken'])["users"][0]["emailVerified"]
                if(not verified):
                    showAlert("Not verified", "Please verify your account to continue.", "Failed")
                    auth.current_user = None
                    return
                self.close()
                chatWindow.display()
            except Exception as e:
                print(e)
                showAlert("Authenticaton Failed", "The email or password may be incorrect", "Failed")
        else:
            fname = self.findChild(QLineEdit,"fname").text()
            lname = self.findChild(QLineEdit,"lname").text()
            email = self.findChild(QLineEdit,"email").text()
            password = self.findChild(QLineEdit,"password_2").text()
            reenter = self.findChild(QLineEdit,"reenter").text()

            if(fname == "" or lname == "" or email == "" or password == "" or reenter == ""):
                showAlert('Incomplete details', 'Please fill all the fields!', 'Error')
                return
            if(password != reenter):
                showAlert('Error', "The passwords don't match!", "Error")
                return
            if(len(password)<8):
                showAlert("Weak password", "Password should be atleast 8 characters long", "Error")
                return
            try:
                user = auth.create_user_with_email_and_password(email, password)
                auth.send_email_verification(user['idToken'])
                showAlert("Information", "We've sen't you an email to verify your account! Please verify your account to continue.", "Success!")
                print(user)
                auth.current_user = None
            except Exception as e:
                showAlert("Error", "User with this email already exists", "Failed")
                return


    





def display():
    app=QApplication(sys.argv)
    welcomeWindow=welcome()
    welcomeWindow.display()
    app.exec_()

if __name__ == "__main__":
    display()
    
    

