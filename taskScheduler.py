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
import numpy
import pickle
#API end 
def Train_and_Send_Model(): 
    # if(date.today().day != 1):
    #     return
    #train the MOdel for new  
    model  = train.Train()

    #Sending the Model Parameters to the server  
    search_api_url = "https://insight-middleware-service.herokuapp.com/send-model"
    data = {'email':'taranggarlapally@gmail.com',
        'classes_': model.classes_.tolist() ,
        'coef_':model.coef_.tolist() ,
        'intercept_': model.intercept_.tolist() ,
        'n_iter_': model.n_iter_.tolist()}

    resp  = requests.post(url = search_api_url, json=data)
    #print(resp   , "response of POST request" )
    #Model sent to the Server and response recieved

  
    
#Update/ replace the new Model with old one
def Recieve_Model ():
    search_api_url = "https://insight-middleware-service.herokuapp.com/get-best-model"

    resp = requests.get(url = search_api_url).json()
    #update Model at 6 o clock
    #print(resp , "response from GET request")
    vectorizer, model  = classify.get_Vectorizer_model()
    model.classes_ = numpy.array(resp["classes_"])
    model.coef_ = numpy.array(resp["coef_"])
    model.intercept_ = numpy.array(resp["intercept_"])
    model.n_iter_ = numpy.array(resp["n_iter_"])

    filename = 'toxic_msgs_logistic_regression_and_vector.pkl'
    with open(filename, 'wb') as fout:
        pickle.dump((vectorizer, model), fout)
    

#Scheduling the Job for 2:00 Clock 


def schedule_task():
    #Scheduling tasks for updating the local model
    schedule.every().day.at("02:00").do(Train_and_Send_Model)
    schedule.every().day.at("06:00").do(Recieve_Model)
    #taks are scheduled 

    #loop to run pending tasks
    while True : 
        schedule.run_pending()



#uncomment above after
#this can  run the file on a seperate thread
