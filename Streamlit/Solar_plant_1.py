import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from sklearn.ensemble import ExtraTreesRegressor
import pickle as pkl
import streamlit as st


# Generate some example data
dates = pd.date_range(start='2022-09-10', periods=168, freq='H')
solar_plant = pd.read_csv('solar_plant_1.csv')

# Create a DataFrame from the data
# data = pd.DataFrame({'Date': dates, 'X': x, 'Y': y})

# load model 

with open('SOLAR_ETR .pickle', 'rb') as f:
    regressor = pkl.load(f)
print(solar_plant.columns)
print(solar_plant.info())
# print(regressor.get_feature_names())
# # Predict using the regression model
solar_plant['Predicted Y'] = regressor.predict(solar_plant[['InsCap(MW)', 'Total installed capacity KW', 'Nr_modules',
       'Module capacity W', 'Model', 'Nr_inverters', 'Inverter capacity KW',
       'Inverter', 'Tracker_type', 'Orientation', 'precipitation_probability',
       'cloudcover', 'uv_index', 'is_day']])
solar_plant['dates'] = dates
# # Create Streamlit app
st.title('Energy production for solar NR1')

# # Plot prediction in time series format
plt.figure(figsize=(10, 6))
plt.plot(solar_plant['dates'], solar_plant['Predicted Y'], label='Predictions')

plt.xlabel('Date')
plt.ylabel('Predictions')
plt.title('Energy production ')
plt.legend()
st.pyplot(plt)

# Display predictions as a table
st.header('Predictions')
st.dataframe(solar_plant[['dates', 'Predicted Y']].rename(columns={'Predicted Y': 'Y Prediction','dates': 'Dates'}))




# Download predictions as CSV
st.header('Download Predictions')
download_options = ['CSV', 'Excel']
chosen_format = st.selectbox("Select download format", download_options)
if st.button('Download'):
    if chosen_format == 'CSV':
        solar_plant[['dates', 'Predicted Y']].to_csv('predictions.csv', index=False)
        st.success("Downloaded predictions as CSV!")
    elif chosen_format == 'Excel':
        solar_plant[['dates', 'Predicted Y']].to_excel('predictions.xlsx', index=False)
        st.success("Downloaded predictions as Excel!")