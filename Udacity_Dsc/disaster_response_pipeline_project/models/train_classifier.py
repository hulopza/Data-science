import sys
import pandas as pd
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
nltk.download(['punkt', 'wordnet', 'averaged_perceptron_tagger', 'omw-1.4'])
import re
from sklearn.multioutput import MultiOutputClassifier
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
import pickle

#Function to load Messages_categories table from database
def load_data(database_filepath):
     """
     Function that loads the table for the model to train.



     Parameters:
     database_filepath: filepath where to find the desired table 'Messages_categories'

     Returns:
     X: Message column with all messages to vectorize for training
     Y: All class binary columns for training the model
     category_names: All names of the categories that the model can predict
     """



     df = pd.read_sql_table('Messages_categories', 'sqlite:///'+ database_filepath)
     X = df['message']
     Y = df.iloc[:,3:]
     category_names = Y.columns

     return X, Y, category_names

#Tokenize function for pipeline
def tokenize(text):
     """
     Function that tokenizes each word
     Removes all punctuation and lemmatizes words with WordNetLemmatizer
     Lower cases and strips the words and appends to clean list



     Parameters:
     text: The text to be tokenized

     Returns:

     clean_tokens: list of clean tokens for the given text
     """





     text = re.sub(r"[^a-zA-Z0-9]", " ", text.lower())#Remove punctuation
     lemmatizer = WordNetLemmatizer() #Lemmatize words
     tokens = word_tokenize(text) # tokenize each word in the message
     clean_tokens = []
    
     for token in tokens:
        clean_token = lemmatizer.lemmatize(token).strip()
        clean_tokens.append(clean_token)
    
     return clean_tokens #return list of clean tokens for the given message



#Function that defines the pipeline and parameters to use in GridSearch
def build_model():

    """
     Function that builds prediction model

     create a pipeline for the data to be processed and creates model object with 
     GridSearch for training the model



     Parameters:
     None

     Returns:

     model: Object for training X and Y data
     """

    pipeline = Pipeline(steps=[
            ('vect_tfidf', TfidfVectorizer(tokenizer=tokenize)),
            ('model', MultiOutputClassifier(LogisticRegression(max_iter=500))) 
        ])

    parameters = {
    'vect_tfidf__ngram_range': ((1,1), (1,2)),
     'model__estimator__class_weight': (None, 'balanced')
    }

    model = GridSearchCV(pipeline, param_grid=parameters)
    
    
    return model


#Function that shows the precission per class and the overall model score, and the best parameters found by gridsearch
def evaluate_model(model, X_test, Y_test, category_names):
    """
     Function that evaluates the model prediction scores and best parameters

     shows the best barameters found by GridSearchCV, the precission of the model per class and the model score





     Parameters:
     None

     Returns:

     None
     """

    
    
    y_pred = model.predict(X_test)
    precission = (y_pred == Y_test).mean()
    best_param = model.best_params_

    print('Best parameters are: ', best_param)
    print('Precission is: ', precission)
    print('Model score: ', model.score(X_test, Y_test))
   

#Function that saves model as a pickle file
def save_model(model, model_filepath):

     """
     Function that saves trained model into pkl file


     Parameters:

     model: trained model
     model_filepath: filepath to save pkl file

     Returns:
     None
     """

     pickle.dump(model, open(model_filepath, 'wb'))
    


def main():
    
     """
     Function that runs all the model training

     Loads data and trains model with pipeline and gridsearch


     Parameters:

     model: trained model
     model_filepath: filepath to save pkl file

     Returns:
     None
     """
     if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.33)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

     else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()