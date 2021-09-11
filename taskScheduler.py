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
    train.Train()

    #Sending the Model Parameters to the server 
    vectorizer , model  = classify.get_Vectorizer_model()
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
        "n_iter_": model.n_iter_ 
    }

    response = requests.post(search_api_url, headers=headers, params=params)
    #Model sent to the Server and response recieved

    #Update/ replace the new Model with old one
    #code

#Scheduling the Job for 2:00 Clock 

schedule.every().day.at("02:00").do(Train_and_Send_Model)


# while True : 
#     schedule.run_pending()

#uncomment above after
#this can  run the file on a seperate thread
