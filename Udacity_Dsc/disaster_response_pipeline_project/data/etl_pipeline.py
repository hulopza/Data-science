#Import necessary libraries

import sys
import pandas as pd
import numpy as np
from sqlalchemy import create_engine



#Function that takes two csv file paths, mereges tha data and returns a dataframe ready for cleaning

def load_data(messages_filepath, categories_filepath):

    """
    Function that loads data for cleaning

    Function loads tables from csv files and prepares for cleaning by converting
    class categories to binary.
    Drops any columns that have the same value in all rows, this to ensure no errors in training

    Parameters:
    messages_filepath: filepath of csv file for the messages.
    categories_filepath: filepath of csv file for categories.

    Returns:
    df: dataframe with merged messages and categories with binary class values.

    """




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


    #-Convert category values to numbers and drop columns with same values in all rows

    for column in categories_df:
        #set each value to be the last character of the string, converting to integer as well
        categories_df[column] = [categories_df[column][x].split('-')[1] for x in range(len(categories_df[column]))]

        #convert column from string to numeric

        categories_df[column] = pd.to_numeric(categories_df[column])
        #drop all columns which sum is equal to the df length or which sum is zero
        if categories_df[column].sum() == len(categories_df) or categories_df[column].sum()==0:

            categories_df.drop(column, axis=1, inplace=True)



    #Replace categories column in df with new category columns

    df.drop('categories', axis=1, inplace=True) #Drop previous categories column
    df = pd.concat([df, categories_df], axis=1) #Concatenate the original dataframe with the new "categories_df" dataframe
    df.reset_index(inplace=True)
   




    return df 

# Funcion to clean dataframe (remove duplicates and prepare dataframe for prediction model)

def clean_data(df):
    
    """
    Function that cleans data prepared for training.

    Drops all duplicated rows and any that are not binary (1, 0)
    Drops unecessary columns 'id' and 'original'   

    Parameters:
    df: dataframe with messages and categories ready for training

    Returns:
    df: dataframe with merged messages and categories with binary class values.

    """



    #check for duplicates
    
    if len(df[df.duplicated() == True]) > 0:
        
        df = df[df.duplicated()==False].copy() #Update df to only unique rows

    
    
    #Drop all rows that have value 2 instead of 0 or 1
    
    index_lst = [] #Index list to drop all values 

    #Loop to get all index values
    for column in df:
        for i in range(len(df)):
             if df[column][i]==2:
                 index_lst.append(i)

    
    df.drop(index_lst, inplace=True) #Drop all rows with "2" values
           
       
    

                



    #Drop "id" and "original" columns, not needed for model
    df.drop(['id', 'original'], axis=1, inplace=True)

  
    
    return df


    

#Function that saves Messages_categories table into a sqlite database
def save_data(df, database_filepath):


    """
    Function saves dataframe to database

    Saves new table as 'Messsages_categories'
    If a table already exists it replaces it with the new df


    Parameters:
    df: dataframe with messages and categories ready for training
    database_filepath: Where to store the new table

    Returns:
    None
    """
    engine = create_engine('sqlite:///'+database_filepath) #Create a SQL engine to save table to
    df.to_sql('Messages_categories', engine, index=False, if_exists='replace')




def main():


    """
    Function that executes all the ETL functions

    Extracts data from csv file paths.
    Transforms and cleans the data for training.
    Loads the data into the new database


    Parameters:
    None

    Returns:
    None
    """

    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df_final = clean_data(df)
        print('Data saved head:' ,df_final.head())
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df_final, database_filepath)
        
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