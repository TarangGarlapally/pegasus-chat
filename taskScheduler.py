'''
Scheduled task{ 
    1. Every Month 1st mid 2 o'clock. 
    2. Job{
        Model m  = trainForNew() ; 
        sendModel(m , hyperparameters... , ) ; // API Call to server POST
            or 
        sendModelFile("FileName") ; 
    }
}
'''
from datetime import date
import train

import schedule 

#API 
import requests 
import classify
#API end 
def Train_and_Send_Model(): 
    if(date.today().day != 1):
        return
    #train the MOdel for new  
    model  = train.Train()

    #Sending the Model Parameters to the server 
    api_key = "api_Key_from_env" 
    search_api_url = "api_url_to_get_universal_model"
    headers = {
        'Authorization': "api_key_with_format" , 
        'Content-Type': 'application/text'
    }
    params  = {
        "classes_": model.classes_, 
        "coef_" :  model.coef_,  
        "intercept_": model.intercept_, 
        "n_iter_": model.n_iter_,
        "type" : "send"
    }
    print("sending API request in task")
    #response = requests.post(search_api_url, headers=headers, params=params)
    #Model sent to the Server and response recieved

    #Update/ replace the new Model with old one
    #code

def Recieve_Model ():
    api_key = "api_Key_from_env" 
    search_api_url = "api_url_to_get_universal_model"
    headers = {
        'Authorization': "api_key_with_format" , 
        'Content-Type': 'application/text'
    }
    params = {
        "type" : "Recieve"
    }
    response = requests.post(search_api_url, headers=headers, params=params)

#Scheduling the Job for 2:00 Clock 


def schedule_task():
    schedule.every().day.at("16:08").do(Train_and_Send_Model)
    print("Task is Scheduled")
    while True : 
        print("here")
        schedule.run_pending()
#schedule.every().day.at("06:00").do(Recieve_Model)



#uncomment above after
#this can  run the file on a seperate thread
