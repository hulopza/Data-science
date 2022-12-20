# Disaster Response Pipeline Project
## Project summary:
The project consits in building a machine learning pipeline of disaster response messages.

### Files in repository:
- **data** folder holds the etl_pipeline.py file which combines and cleans the disaster_categories.csv and disaster_messages.csv  files. It then loads the table into a sqlite database (DisasterResponse.db) to be accessed by the classifier code.
  

- **models** folder conatins the train_classifier.py file which trains the multioutput classification model using gridsearch to find the best parameters. The model then outputs the precission, recall, f1-score and support for each label.


## Instructions:
1. Run the following commands in the project's root directory to set up your database and model.

    - To run ETL pipeline that cleans data and stores in database
        `python data/etl_pipeline.py data/disaster_messages.csv data/disaster_categories.csv data/DisasterResponse.db`
    - To run ML pipeline that trains classifier and saves
        `python models/train_classifier.py data/DisasterResponse.db models/classifier.pkl`

2. Run the following command in the app's directory to run your web app.
    `python run.py`

3. Go to http://0.0.0.0:3001/
