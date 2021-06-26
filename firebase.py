import pyrebase
from dotenv import dotenv_values

env = dotenv_values(".env")

def init():
	firebaseConfig = {
	    "apiKey": env["apiKey"],
	    "authDomain": env["authDomain"],
	    "projectId": env["projectId"],
	    "storageBucket": env["storageBucket"],
	    "messagingSenderId": env["messagingSenderId"],
	    "appId": env["appId"],
	    "measurementId": env["measurementId"],
	    "databaseURL": env["databaseURL"]
	}

	return pyrebase.initialize_app(firebaseConfig)
