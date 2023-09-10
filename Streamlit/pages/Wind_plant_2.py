import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from sklearn.ensemble import ExtraTreesRegressor
import pickle as pkl
import streamlit as st

import requests

def get_weather_forecast(lat: float, long: float):
    resp = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=temperature_2m,surface_pressure,windspeed_10m,winddirection_10m&windspeed_unit=ms&timezone=auto')
    df = pd.DataFrame.from_dict(resp.json()['hourly'])
    df.rename(columns={'temperature_2m': 'temp', 'surface_pressure':'pressure',  'windspeed_10m':'wind_speed (m/s)',  'winddirection_10m':'wind_dir'}, inplace=True)
    df.drop(['time'], axis=1, inplace=True)
    return df


# Generate some example data
dates = pd.date_range(start='2022-09-10', periods=168, freq='H')
wind = pd.read_csv('VI.csv')
wind = wind[wind['wind_plant']=='Unit2'].reset_index()
lat, long = wind[['latitude', 'longitude']].iloc[0]
print(lat, long)
wind = wind[wind['wind_plant']=='Unit2']
weather_df = get_weather_forecast(lat, long)
print(weather_df.head())
for cn in ['temp',  'pressure',  'wind_speed (m/s)',  'wind_dir']:
    len(wind[cn])
    wind[cn] = weather_df[cn]

# load model 
with open('ETR.pickle', 'rb') as f:
    regressor = pkl.load(f)

print(wind[['wind_speed (m/s)', 'wind_dir', 'temp', 'pressure', 'Turbine Model',
       'Tower Height', 'Rotor Diameter', 'Production Year', 'START m/s',
       'STOP  m/s', 'Service', 'MaxLimit']].info())

# Predict using the regression model
wind['Predicted Y'] = regressor.predict(wind[['wind_speed (m/s)', 'wind_dir', 'temp', 'pressure', 'Turbine Model',
       'Tower Height', 'Rotor Diameter', 'Production Year', 'START m/s',
       'STOP  m/s', 'Service', 'MaxLimit']])
print(len(wind))
wind['dates'] = dates

# # # Create Streamlit app
st.title('Energy production for wind NR2')

# # # Plot prediction in time series format
plt.figure(figsize=(10, 6))
plt.plot(wind['dates'], wind['Predicted Y'], label='Predictions')

plt.xlabel('Date')
plt.ylabel('Predictions')
plt.title('Energy production ')
plt.legend()
st.pyplot(plt)

# Display predictions as a table
st.header('Predictions')
st.dataframe(wind[['dates', 'Predicted Y']].rename(columns={'Predicted Y': 'Y Prediction','dates': 'Dates'}))




# Download predictions as CSV
st.header('Download Predictions')
download_options = ['CSV', 'Excel']
chosen_format = st.selectbox("Select download format", download_options)
if st.button('Download'):
    if chosen_format == 'CSV':
        wind[['dates', 'Predicted Y']].to_csv('predictions.csv', index=False)
        st.success("Downloaded predictions as CSV!")
    elif chosen_format == 'Excel':
        wind[['dates', 'Predicted Y']].to_excel('predictions.xlsx', index=False)
        st.success("Downloaded predictions as Excel!")