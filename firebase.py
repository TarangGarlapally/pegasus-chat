import pyrebase

def init():
	firebaseConfig = {
	    "apiKey": "AIzaSyAwP_J2UEIX7gO2fIL1Ovx1fDcR-g5QVDg",
	    "authDomain": "pegasuschat.firebaseapp.com",
	    "projectId": "pegasuschat",
	    "storageBucket": "pegasuschat.appspot.com",
	    "messagingSenderId": "1084666068688",
	    "appId": "1:1084666068688:web:4505625e8d5f298a8728d5",
	    "measurementId": "G-MRP0J0SQLZ",
	    "databaseURL": "https://pegasuschat-default-rtdb.firebaseio.com"
	}

	return pyrebase.initialize_app(firebaseConfig)
