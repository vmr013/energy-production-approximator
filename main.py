import requests as rq
import streamlit as st
import data
import pickle as pkl
import datetime
import pandas as pd
from matplotlib import pyplot as plt

label_encoding = {
    'SOLAR': {
        'models': {
            '600W Risen 120-8-600M': 0
        },
        'inverters': {
            'GROWATT MAX 110 KTL3-X LV': 0
        },

    },
    'WIND': {'models': {
        "NORDEX N60": 3,
        "General Electric 1.5S": 2,
        "Enercon E66 1,8/70": 0,
        "SUEDWIND S70": 5,
        "General Electric": 1,
        "SUDWIND S70": 4,

    }}
}


def get_weather_forecast(plant, start_date, end_date, columns, rename=None, drop=None):
    response = rq.get(
        f'https://api.open-meteo.com/v1/forecast?'
        f'latitude={plant.geolocation.latitude}&longitude={plant.geolocation.longitude}'
        f'&hourly={columns}&windspeed_unit=ms&timezone=auto'
        f'&start_date={start_date.strftime("%Y-%m-%d")}&end_date={end_date.strftime("%Y-%m-%d")}')
    weather_data = response.json()
    weather_df = pd.DataFrame.from_dict(weather_data['hourly'])
    if rename is not None:
        weather_df.rename(
            columns=rename, inplace=True)
    if drop is not None and len(drop):
        weather_df.drop(drop, axis=1, inplace=True)
    return weather_df


def load_model(plant_type):
    if 'models' in st.session_state:
        models = st.session_state['models']
    else:
        models = st.session_state['models'] = {}
    model = models.get(plant_type)
    if model is None:
        with open(f'models/{plant_type}_ETR.pickle', 'rb') as f:
            model = pkl.load(f)
            models[plant_type] = model
    return model


def estimate_energy(plant, start_date, period_span, model):
    dates = pd.date_range(start=start_date, periods=period_span * 24, freq='h')
    if plant.type == 'SOLAR':
        weather_df = get_weather_forecast(plant, start_date, dates[-1],
                                          'precipitation_probability,cloudcover,uv_index,is_day')
        prediction_data = []
        for row in weather_df.index:
            row = weather_df.loc[row]
            prediction_data.append(
                [plant.installationCapacity, plant.totalCapacity, plant.numberOfModules, plant.moduleCapacity,
                 label_encoding[plant.type]['inverters'][plant.inverter], plant.numberOfInverters,
                 plant.inverterCapacity, label_encoding[plant.type]['models'][plant.model],
                 0, 0,
                 row.precipitation_probability, row.cloudcover, row.uv_index, row.is_day])
        prediction_df = pd.DataFrame(prediction_data)
        prediction_df['Predicted Y'] = model.predict(prediction_df)
        prediction_df['dates'] = dates
        plt.figure(figsize=(10, 6))
        plt.plot(prediction_df['dates'], prediction_df['Predicted Y'], label='Predictions')
        plt.xlabel('Date')
        plt.xticks(rotation=90)
        plt.ylabel('Production (MW)')
        plt.title(f'{plant.type.title()} energy production estimation')
        plt.legend()
        st.pyplot(plt)
    elif plant.type == 'WIND':
        weather_df = get_weather_forecast(plant, start_date, dates[-1],
                                          'temperature_2m,surface_pressure,windspeed_10m,winddirection_10m',
                                          {'temperature_2m': 'temp', 'surface_pressure': 'pressure',
                                           'windspeed_10m': 'wind_speed (m/s)',
                                           'winddirection_10m': 'wind_dir'},
                                          ['time']
                                          )
        prediction_data = []
        for row in weather_df.index:
            row = weather_df.loc[row]
            prediction_data.append(
                [row['wind_speed (m/s)'], row.wind_dir, row.temp, row.pressure,
                 label_encoding[plant.type]['models'][plant.model], plant.towerHeight,
                 plant.rotorDiameter, plant.productionYear, plant.startSpeed, plant.stopSpeed, 0, plant.maxLimit])
        prediction_df = pd.DataFrame(prediction_data)
        prediction_df['Predicted Y'] = model.predict(prediction_df)
        prediction_df['dates'] = dates
        plt.figure(figsize=(10, 6))
        plt.plot(prediction_df['dates'], prediction_df['Predicted Y'], label='Predictions')
        plt.xlabel('Date')
        plt.xticks(rotation=90)
        plt.ylabel('Production (MW)')
        plt.title('Eolian energy production estimation')
        plt.legend()
        st.pyplot(plt)
    else:
        st.error('Unsupported power plant type!')


def render_plant(plant: data.SolarPlant | data.WindPlant):
    st.button(':material/arrow_back: Back', on_click=st.session_state.pop, args=('plant', None))
    render_plant_name(plant)
    model = load_model(plant.type)
    columns = st.columns(2)
    with columns[0]:
        start_date = st.date_input('Estimation Start Date', min_value=datetime.datetime.today())
    with columns[1]:
        period_span = st.number_input('Estimation period (in days)', min_value=1, max_value=12, step=1)
    estimate_energy(plant, start_date, period_span, model)


def main(number_of_columns=3):
    if 'plant' in st.session_state:
        render_plant(st.session_state['plant'])
        return
    columns = st.columns(number_of_columns)
    if 'plants' not in st.session_state:
        st.session_state['plants']: data.PowerPlants = data.get_power_plants()
    for i, plant in enumerate(st.session_state['plants'].root):
        with columns[i % number_of_columns]:
            with st.container():
                render_plant_name(plant)
                st.subheader(f"Model: {plant.model}", anchor=False)
                st.link_button(f'Geolocation: {plant.geolocation.string}',
                               url=f"https://www.google.com/maps/place/"
                                   f"{plant.geolocation.latitude},{plant.geolocation.longitude}",
                               icon=":material/location_on:")
                st.button('See estimations', key=f'plant-{i}', icon=":material/wifi_channel:",
                          on_click=st.session_state.update, args=({'plant': plant},))


def render_plant_name(plant):
    if plant.type == 'WIND':
        icon = ":blue[:material/wind_power:]"
    elif plant.type == 'SOLAR':
        icon = ':orange[:material/sunny:]'
    else:
        icon = ":material/question_mark:"
    st.title(icon + plant.name, anchor=False)


def about():
    st.title(':blue[:material/info:]About', anchor=False)


if __name__ == '__main__':
    st.set_page_config(
        page_title='Energy Production Estimator',
        page_icon=":bulb:",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    pg = st.navigation([
        st.Page(main, title='Home'),
        st.Page(about, title='About')
    ])
    pg.run()
