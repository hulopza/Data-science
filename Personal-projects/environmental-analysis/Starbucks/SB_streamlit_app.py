from matplotlib import pyplot as plt
import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import geopandas as gpd


#Test to upload to repository
unit = ''  
column = ''
st.title('World Water & Carbon tracker')

st.write('Please choose country and category to analyse')

st.subheader('Category')
mapoption = st.selectbox('Choose impact category', ['Carbon', 'Water'])
  





#Process and create data tables
@st.cache
def get_map_data():
  current_CO2data = pd.read_csv('./Starbucks/co2WorldData.csv')
  current_CO2data = current_CO2data.rename(columns = {"Entity":"Country"})
  current_CO2data = current_CO2data[current_CO2data['Year']==2020]
  current_waterdata = pd.read_csv('./Starbucks/annual-freshwater-withdrawals.csv')
  current_waterdata = current_waterdata.rename(columns = {"Entity":"Country"})
  #current_waterdata = current_waterdata[current_waterdata['Year']==2017]

  json_file = './Starbucks/custom.geo.json'
  geo_df = gpd.read_file(json_file)
  dict = {'United States of America':'United States'}

  geo_df= geo_df.rename(columns = {"sovereignt":"Country"})
  geo_df['Country'].replace(dict, inplace = True)

  return current_CO2data, geo_df, current_waterdata










@st.cache(hash_funcs={folium.folium.Map: lambda _: None}, allow_output_mutation=True)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
def create_choromap(_geo_data, CO2_data, combined_geo_CO2Data, footprint, unit, color, column):


  m = folium.Map(location=[48, -102], zoom_start=3)
  
  folium.Choropleth(
    geo_data=_geo_data,
    name= "%s footprint"%(footprint),
    data=CO2_data,
    columns=["Country", column],#Things will be more complex, need to think how to establish default columns
    key_on="properties.Country",
    fill_color=color,
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="%s footprint (%s)"%(footprint, unit),
    nan_fill_color = "white",
    highlight = True,
    nan_fill_opacity = 1
    ).add_to(m)
          


  


 #Add hover function 
  style_fun = lambda x: {'fillColor': '#ffffff', 
                            'color':'#000000', 
                            'fillOpacity': 0.1, 
                            'weight': 0.1}
  highlight_fun = lambda x: {'fillColor': '#000000', 
                                'color':'#000000', 
                                'fillOpacity': 0.50, 
                                'weight': 0.1}

  NIL = folium.features.GeoJson(
    data = combined_geo_CO2Data,
    style_function=style_fun, 
    control=False,
    highlight_function=highlight_fun, 
    tooltip=folium.features.GeoJsonTooltip(
        fields=['Country',column],
        aliases=['Country',unit],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
    )
  )
  m.add_child(NIL)
  

  return m


#Main data variables
CO2data = get_map_data()[0]
geo_df = get_map_data()[1]
WaterData = get_map_data()[2]

#Carbon map variables
CO2_data = CO2data.groupby('Country')['Cumulative CO2 emissions'].sum().to_frame().reset_index()
CO2_data['Cumulative CO2 emissions'] = round(CO2_data['Cumulative CO2 emissions']/1000000000,2)
combined_geo_CO2Data = geo_df.merge(CO2_data, on = 'Country', how = 'left')
carbon_map = create_choromap(geo_df,CO2_data,combined_geo_CO2Data, 'CO2e', 'Cumulative tCO2 (billion)', "YlOrRd", "Cumulative CO2 emissions" )

#Water map variables
Water_data = WaterData.groupby('Country')['Water usage billion m3'].sum().to_frame().reset_index()
Water_data['Water usage billion m3'] = round(Water_data['Water usage billion m3']/1000000000,2)
combined_geo_WaterData = geo_df.merge(Water_data, on = 'Country', how = 'left')
water_map = create_choromap(geo_df,Water_data,combined_geo_WaterData, 'Water usage', 'Cumulative m3 (billion)', "GnBu", "Water usage billion m3")


st.subheader('Map, cumulative values up to 2020')

#Map for CO2 emissions
if mapoption=='Carbon':
  folium_static(carbon_map)

#Map for water impact
else:
  
  folium_static(water_map)

st.subheader('Country analysis per year')

##############################################################################################################################################
#Create functions for plots
@st.cache
def get_plot_data():
    current_CO2data = pd.read_csv('./Starbucks/co2WorldData.csv')
    current_CO2data = current_CO2data.rename(columns = {"Entity":"Country"})
    current_waterdata = pd.read_csv('./Starbucks/annual-freshwater-withdrawals.csv')
    current_waterdata = current_waterdata.rename(columns = {"Entity":"Country"})

    return current_CO2data, current_waterdata

CO2_plot_Data = get_plot_data()[0]
Water_plot_Data = get_plot_data()[1]


def plot_country(country, footprint):
    
    if footprint == 'Carbon':
        
        PlotData = CO2_plot_Data[CO2_plot_Data['Country']==country]
        y = PlotData['Cumulative CO2 emissions']/1000000000
        title = "%s Cumulative CO2 emissions"%country
        y_label = 'Billion tCO2'
        
        
    else: 
        PlotData = Water_plot_Data[WaterData['Country']==country]
        y = PlotData["Water usage billion m3"]/1000000000
        title = "%s yearly water usage"%country
        y_label = 'Trillion m3'
        
        
    x = PlotData['Year']
    

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title(title)
    ax.set_ylabel(y_label)
    
    ax.set_xlabel('Year')
    ax.ticklabel_format(style='plain')
    
    
    return fig


option_list = CO2_plot_Data['Country'].unique()

plotoption = st.selectbox('Choose a country to plot', option_list)

fig = plot_country(plotoption, mapoption)


st.pyplot(fig)