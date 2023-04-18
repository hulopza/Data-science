import pandas as pd
import streamlit as st
import numpy as np
import pgeocode 
from geopy.distance import geodesic




##Defining functions

#check if file can be worked on
def Master_calcs(csv):
    
    #Check distance:
    if len(csv.iloc[:,2][1])!= 2 or len(csv.iloc[:,2][1]):
        response = 'Your Country codes must be 2 letters long. Please upload csv as the example.'
        
    else:
        response = getDistance(csv)
        
    return response 


#####Parser
def parse_csv(csv):
    travel_list = []
    for i in range(len(csv)):
        string = str(csv.iloc[i,0]) + '|' + str(csv.iloc[i,1]) + '.' + str(csv.iloc[i,2]) + '|' + str(csv.iloc[i,3])
        travel_list.append(string)
        
        
    unique_travel_list = np.unique(travel_list)
    country_1_lst = []
    country_2_lst = []
    Zip_1_lst = []
    Zip_2_lst = []
        
    for i in range(len(unique_travel_list)):
        dest_list = unique_travel_list[i].split('.')
        
        for j in range(len(dest_list)):
            
            if j%2 == 0:
                item = dest_list[j].split('|')
                country_1_lst.append(item[0])
                Zip_1_lst.append(item[1])
            else:
                item = dest_list[j].split('|')
                country_2_lst.append(item[0])
                Zip_2_lst.append(item[1])
        
    return country_1_lst, country_2_lst, Zip_1_lst, Zip_2_lst, unique_travel_list, travel_list


###Table builder

def buildFinaltable(parsed_lists, csv, distance_list):
    distance_lst = []
    unique_travel_lst = parsed_lists[4]
    
    for i in range(len(csv)):
        istring =str(csv.iloc[i,0]) + '|' + str(csv.iloc[i,1]) + '.' + str(csv.iloc[i,2]) + '|' + str(csv.iloc[i,3])
        
        for j in range(len(unique_travel_lst)):
            if istring == unique_travel_lst[j]:
                distance_lst.append(distance_list[j])
                
                
    csv["Distance (km)"] = distance_lst
    
    return csv

###Distance calculator

def getDistance(csv):
    
    parsed_lists = parse_csv(csv)
    country_1_lst = parsed_lists[0]
    country_2_lst = parsed_lists[1]
    Zip_1_lst = parsed_lists[2]
    Zip_2_lst = parsed_lists[3]
    distance_list = []
    
    for i in range(len(country_1_lst)):
     
     
     try:
       nomii = pgeocode.Nominatim(country_1_lst[i])
       nomij = pgeocode.Nominatim(country_2_lst[i])
       first_location = [nomii.query_postal_code(Zip_1_lst[i]).latitude, nomii.query_postal_code(Zip_1_lst[i]).longitude]
       second_location = [nomij.query_postal_code(Zip_2_lst[i]).latitude, nomij.query_postal_code(Zip_2_lst[i]).longitude]
       distance_list.append((geodesic(first_location, second_location).kilometers)*1.18) #1.18 is correction factor for road distance taken from SP internal tool
      
     except:
       
       distance_list.append('Not found')
     
      
                   
                   
    Final_table = buildFinaltable(parsed_lists, csv, distance_list)
    
    return  Final_table
                   

def DistanceCalcs():
    st.title('Welcome to the Zip code distance calculator!')
    st.subheader('Please upload your data as shown below as CSV to calculate the distance between two locations.')
    st.subheader('Please make sure your country code is ISO 2 digit code')

    example = {'Origin country ISO code': ['US', 'MX', 'GT'], 'Origin country Zip code':[52140,45886,1114]

    , 'Destination country ISO code': ['MX', 'GT', 'US'], 'Destination country zip code': [44448, 12529, 35468]}

    st.table(example)


    example['Distance (km)'] = [45555, 11123, 44448]



    file = st.file_uploader('Upload your CSV here')
    

    st.subheader('Your finished table should look like this :)')

    st.table(example)

   

    if file:
        try:
             file = pd.read_csv(file)
             result = getDistance(file)
             result = result.to_csv()
             st.download_button('Download results', result, 'Final_table.csv', 'text/csv')
        except:
            
            st.warning("The calculations returned an error. Please check the following and try again:\n - All countries have the correct ISO 2 digit code \n - All zip codes are correct \n - All data in cells are trimmed")
            
            
       

DistanceCalcs()

with open('./DistancefromZipcode/TestDistance.csv') as f:
    st.download_button('Download a sample file for testing',f, 'TestFile.csv', 'text/csv' )




