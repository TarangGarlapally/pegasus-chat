from PyQt5 import QtWidgets,uic
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QTimer, QThread
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QLineEdit,QMainWindow, QMessageBox,QPushButton, QScrollArea ,QSizePolicy, QWidget, QVBoxLayout
import sys,time,os
import time,functools
import datetime
import threading
import math
from dns.message import MessageSection
import firebase
import stream
import mysql_pegasus as db
import classify

'''
Firebase part
'''
firebase = firebase.init()
auth = firebase.auth()
user = "none"
rtdb = firebase.database()



'''
Firebase part end
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
def own_message_label(chat,message):
    text=message["message"]
    sent=message["sent"]
    time=message["time"]
    isToxic=message["Toxic"]
    isVisible=message["Visible"]
    hbox=QHBoxLayout()
    label=QLabel(text)
    label.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
    
    label.setMaximumWidth(450)
    label.setMinimumHeight(60)
    label.setWordWrap(True)
    if sent:
        label.setStyleSheet("background-color:#333399;color:#fff;font-size:20px;margin:15px 0px 15px 0px;padding:5px;border:0px solid transparent;border-radius:5px")
        label.setAlignment(Qt.AlignRight)
        hbox.addStretch(1)
        hbox.addWidget(label)
    else:
        label.setAlignment(Qt.AlignLeft)
        if isToxic:
            label.setStyleSheet("background-color:red;color:#fff;font-size:20px;margin:15px 0px 15px 0px;padding:5px;border:0px solid transparent;border-radius:5px")
            label.setAlignment(Qt.AlignLeft)
            if isVisible:
                label.mousePressEvent = functools.partial(chat.reportNonToxic,time=time)
                label.setAlignment(Qt.AlignLeft)
            else:
                label.setText("Potential Toxic Message. Click to View")
                label.mousePressEvent = functools.partial(chat.viewMessage,time=time)
                label.setAlignment(Qt.AlignLeft)
        else:
            label.setStyleSheet("background-color:#333399;color:#fff;font-size:20px;margin:15px 0px 15px 0px;padding:5px;border:0px solid transparent;border-radius:5px")
            label.mousePressEvent = functools.partial(chat.reportToxic,time=time)
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
        self.findChild(QLineEdit,"email").returnPressed.connect(lambda state,chatWindow=chatWindow: self.next(chatWindow))
        self.findChild(QLineEdit,"fname").returnPressed.connect(lambda state,chatWindow=chatWindow: self.next(chatWindow))
        self.findChild(QLineEdit,"lname").returnPressed.connect(lambda state,chatWindow=chatWindow: self.next(chatWindow))

        
        '''
        returning to chatWindow
        '''
        self.findChild(QPushButton,"addcontactButton").clicked.connect(lambda state,chatWindow=chatWindow: self.next(chatWindow))
    
    def next(self,chatWindow):
        contact = self.findChild(QLineEdit,"email").text()
        fname = self.findChild(QLineEdit,"fname").text()
        lname = self.findChild(QLineEdit,"lname").text()
        if(fname == "" or lname == "" or contact == "" ):
                showAlert('Incomplete details', 'Please fill all the fields!', 'Error')
                return
        receiver = rtdb.child("users").order_by_child("email").equal_to(contact).get()
        for user in receiver.each():
            receiver = user.val()
            db.insertContact(receiver["email"], receiver["fname"], receiver["lname"])
            break
        else:
            showAlert("Not found", "User not found! Invite them to use this app!", "Error")
        chatWindow.renderContacts()
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
        self.renderContacts()

        
        '''
        Adding previous messages
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
        self.findChild(QPushButton,"addButton").clicked.connect(self.add)

        '''
        Below is the code for updating messageSection based on the contact selected
        '''    


    def renderContacts(self):
        contacts = db.getContacts()
        self.contacts=contacts
        self.contactsList=self.findChild(QVBoxLayout,"contactsList")
        self.deleteItems(self.contactsList)
        for contact in self.contacts:
            self.contactsList.addWidget(own_push_button(contact[0]))
        self.contactButtons=[]
        for contact in self.contacts:
            name=contact[0]
            self.contactButtons.append(self.findChild(QPushButton,name))

        mapping=[]
        for i in range(0,len(self.contacts)):
            mapping.append((self.contactButtons[i],self.contacts[i][0]))
        for button,name in mapping:
            button.clicked.connect(lambda state,name=name: self.messageSection(name))

    def messageSection(self,name):
        if name==None or name=="":
            pass
        else:
            self.findChild(QLabel,"headName").setText(name)
            self.deleteItems(self.vlayout)

            messages=db.getMessages(name)
            if len(messages)!=0:
                for message in messages:

                    #test for toxicity
                    #isToxic = classify.checkIfToxic(message["message"])

                    self.vlayout.addLayout(own_date_label(message['time']))
                    self.vlayout.addLayout(own_message_label(self,message))
            self.timer = QTimer()
            self.timer.timeout.connect(lambda name=name: self.messageSection(name)) 
            self.timer.setInterval(2000)
            self.timer.start()


    '''
    Below is the code for reporting a message as toxic
    '''

    def reportToxic(self,event,time=None):
        response = QMessageBox.question(self, 'Report', "Report this message as toxic?", QMessageBox.Yes | QMessageBox.No)
        if response == QMessageBox.Yes:
            db.reportToxic(time)
            self.messageSection(self.findChild(QLabel,"headName").text())
        else:
            print("Not reported")


    '''
    Below is the code for reporting a message as Non-toxic
    '''

    def reportNonToxic(self,event,time=None):
        response = QMessageBox.question(self, 'Report', "Report this message as Non-toxic?", QMessageBox.Yes | QMessageBox.No)
        if response == QMessageBox.Yes:
            db.reportNonToxic(time)
            self.messageSection(self.findChild(QLabel,"headName").text())
        else:
            print("Not reported")
    
    '''
    Below is the code for viewing the message
    '''
    def viewMessage(self,event,time=None):
        response = QMessageBox.question(self, 'View message?', "This message is flagged as 'Toxic'. Want to see it?", QMessageBox.Yes | QMessageBox.No)
        if response == QMessageBox.Yes:
            db.viewMessage(time)
            self.messageSection(self.findChild(QLabel,"headName").text())
        else:
            print("Not viewed")


        
        
    
    def deleteItems(self,layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.deleteItems(item.layout())
        
        
    
    def send(self):
        inputField=self.findChild(QLineEdit,"message")
        message=inputField.text()
        if message!="":
            newMessageLayout=own_message_label(self,message)
            inputField.clear()
            timestamp = math.floor(time.time()*1000)
            self.vlayout.addLayout(own_date_label(timestamp))
            self.vlayout.addLayout(newMessageLayout)
            db.insertMessage(message, "sent", self.findChild(QLabel,"headName").text(), True)
            
            #check if toxic
            classify.checkIfToxic(message)
            
            #send to firebase
            stream.send(rtdb, self.findChild(QLabel,"headName").text(), user["email"], message)
        







        
    
    def add(self):
        addWindow=add()
        addWindow.display(self)


    def display(self):
        self.my_stream = rtdb.child(user["localId"]).stream(lambda x: stream.stream_handler(x, rtdb, user))
        self.show()
        #start ML model
        
    def closeEvent(self, event):
        self.my_stream.close()
        event.accept() # let the window close
        os._exit(0)

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
                my_stream = rtdb.child(user["localId"]).stream(lambda x: stream.stream_handler(x, rtdb, user))
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
                print(user)
                try:
                    rtdb.child("users").child(user["localId"]).set({"email":user["email"], "fname":fname, "lname":lname})
                except Exception as e:
                    print(e)
                showAlert("Information", "We've sen't you an email to verify your account! Please verify your account to continue.", "Success!")
                auth.current_user = None
            except Exception as e:
                showAlert("Error", "User with this email already exists", "Failed")
                return





def display():  
    app=QApplication(sys.argv)
    welcomeWindow=welcome()
    welcomeWindow.display()
    app.exec_()

# def connectToDuet():
#     duet = sy.launch_duet(loopback=True)
#     messages=db.getMessages("taranggarlapally@gmail.com")
#     data=th.tensor([])
#     for message in messages:
#         msg=[]
#         for i in message["message"]:
#             msg.append(ord(i))
#         msg.append(ord("\n"))
#         data=th.cat([data, th.tensor(msg)])
#         break
    
#     data = data.tag("Messages")
#     data = data.describe("Some messages of the user")
#     data_pointer = data.send(duet,searchable=True)
#     print(duet.store.pandas)


if __name__ == "__main__":
    display()

    # connectToDuet()

    
    

