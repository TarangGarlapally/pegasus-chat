import pickle
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
from nltk.corpus import stopwords
import sklearn.feature_extraction.text as ft

stop_words = set(stopwords.words('english'))

vectorizer = ft.TfidfVectorizer(stop_words=stop_words)
model = None
  
filename = 'toxic_msgs_logistic_regression_and_vector.pkl'
with open(filename, 'rb') as f:
    vectorizer, model = pickle.load(f)
print("initialized model")

def checkIfToxic(message):
    df = vectorizer.transform(pd.DataFrame({"words":[message]})["words"])
    result = model.predict(df)
    print(result)
    print(result[0] == 1)
    
    return result[0] == 1