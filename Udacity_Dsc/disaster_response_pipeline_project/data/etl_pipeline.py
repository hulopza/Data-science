#Import necessary libraries

import sys
import pandas as pd
import numpy as np
from sqlalchemy import create_engine



#Function that takes two csv file paths, mereges tha data and returns a dataframe ready for cleaning

def load_data(messages_filepath, categories_filepath):
    #--------------------------------------Loading data from files--------------------------------------------------------
    messages_df = pd.read_csv(messages_filepath)#load messages data
    categories_df = pd.read_csv(categories_filepath)#load categories data
    df = messages_df.merge(categories_df, how='left', on='id') #merge the two dataframes

   

    categories_df = df['categories'].str.split(';', expand=True) #Separate all categories and create one column for each

    #----------------------------------Processing data----------------------------------------------------------------------

    #Updating cateory df column names
    column_names_raw = categories_df.head(1).values.tolist()[0] #Get list of column names 
    category_colnames = [column_names_raw[x].split('-')[0] for x in range(len(column_names_raw))] # map list to remove "-0" and "-1" sections

    categories_df.columns = category_colnames #Update column names for category dataframe


    #-Convert category values to numbers 0 or 1

    for column in categories_df:
        #set each value to be the last character of the string, converting to integer as well
        categories_df[column] = [categories_df[column][x].split('-')[1] for x in range(len(categories_df[column]))]

        #convert column from string to numeric

        categories_df[column] = pd.to_numeric(categories_df[column])


    #Replace categories column in df with new category columns

    df.drop('categories', axis=1, inplace=True) #Drop previous categories column
    df = pd.concat([df, categories_df], axis=1) #Concatenate the original dataframe with the new "categories_df" dataframe




    return df 

# Funcion to clean dataframe (remove duplicates and prepare dataframe for prediction model)

def clean_data(df):
    #check for duplicates
    if len(df[df.duplicated() == True]) > 0:
        df = df[df.duplicated()==False] #Update df to only unique rows

    #Drop "id" and "original" columns, not needed for model
    df.drop(['id', 'original'], axis=1, inplace=True)

    #Update "child_alone" name to child_alone_DUMMY and update values to 1 since these are always 0 in this dataset
    df.rename(columns = {'child_alone' : 'child_alone_DUMMY'}, inplace=True)
    df['child_alone_DUMMY'] = 1


    #Remove all rows with only one class label, model used: MultiOutputClassifier(LogissticRegression()), will not work with only one label
    index_lst = []

    for i in range(len(df)):
        row_sum = df.iloc[i,2:].sum(axis=0)

        if row_sum == 1:
            index_lst.append(row_sum)

    
    #Drop all rows from index_lst

    df.drop(df.iloc[index_lst].index, inplace=True)


    
    return df


    


def save_data(df, database_filepath):
    engine = create_engine(database_filepath) #Create a SQL engine to save table to
    df.to_sql('Messages', engine, index=False)




def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()