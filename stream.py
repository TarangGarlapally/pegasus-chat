import mysql_pegasus as db
import firebase


def checkAndAddMessage(message):
    if(db.isContact(message["sender"])):
        db.insertMessage(message["message"], "received", message["sender"], seen = True)
        return
    # if not contact create contact and then add message

# Firebase realtime db stream handler
def stream_handler(stream):
    print(stream["path"])
    if(stream["data"] == None):
        return
    if(stream["path"] == "/"):
        stream = [(k, v) for k, v in stream["data"].items()]
        for message in stream:
            message = message[1]
            checkAndAddMessage(message)
    else:
        # recieved single message
        message = stream["data"]
        checkAndAddMessage(message)


# firebase = firebase.init()
# rtdb = firebase.database()
# my_stream = rtdb.child("8wsErCz12JaZ3C3HXrHuvi8xDdH2").stream(stream_handler)
# my_stream.close()
