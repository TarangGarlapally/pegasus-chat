'''

Function  TrainForNew(){
    Messages  - message(X)  , toxicity(Y)    #Model + altered 

    new Dataset  - 
    1. convert X to vector 
    2. train based on "Messages" using LogisticRegression
    3. returns newly trained Model. 

}

'''
#ML 
import classify 
import pandas as pd
import numpy as np
#ML end

#DB 
import mysql_pegasus as dbtool 
#DB end  



def Train(): 
    #getting Vectorizer and Model to train
    vectorizer , model  = classify.get_Vectorizer_model()

    #retrieving messages from Internal storage
    messages  = dbtool.getAllMessages()

    words  = list()
    toxic  = list()
    for message in messages : 
        words.append(message['message'])
        toxic.append(message['toxic'])
    
    words  = vectorizer.transform(
        pd.DataFrame({"words":[i for i in words]})["words"]
    )
    model.fit(words , pd.DataFrame({"toxic":[i for i in toxic]})["toxic"])
    return model 

# Train()