import mysql_pegasus as db
import firebase
import frontend






def checkAndAddMessage(rtdb, message):
    if(db.isContact(message["sender"])):
        try:
            db.insertMessage(message["message"], "received", message["sender"], seen = True)
            return
        except Exception as e:
            print(e)
    # if not contact create contact and then add message
    receiver = rtdb.child("users").order_by_child("email").equal_to(message["sender"]).get()
    for user in receiver.each():
        receiver = user.val()
        db.insertContact(receiver["email"], receiver["fname"], receiver["lname"])
        db.insertMessage(message["message"], "received", message["sender"], seen = True)
        break 
    

def send(rtdb, contact, sender, message):
    receiver = rtdb.child("users").order_by_child("email").equal_to(contact).get()
    rid = ""
    for user in receiver.each():
        receiver = user.val()["email"]
        rid = user.key()
        break 
    if(receiver == contact):
        data = {"message": message, "sender": sender}
        rtdb.child(rid).push(data)


# Firebase realtime db stream handler
def stream_handler(stream, rtdb, user,chatWindow):
    print(stream["path"])
    if(stream["data"] == None):
        return
    if(stream["path"] == "/"):
        stream = [(k, v) for k, v in stream["data"].items()]
        for message in stream:
            message = message[1]
            print(message)
            checkAndAddMessage(rtdb, message)
    else:
        # recieved single message
        message = stream["data"]
        checkAndAddMessage(rtdb, message)
    rtdb.child(user["localId"]).remove()
    

# firebase = firebase.init()
# rtdb = firebase.database()
# my_stream = rtdb.child("8wsErCz12JaZ3C3HXrHuvi8xDdH2").stream(stream_handler)
# my_stream.close()
