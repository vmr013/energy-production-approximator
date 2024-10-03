import streamlit as st
import data


def render_plant(plant: data.SolarPlant | data.WindPlant):
    if plant.type == 'WIND':
        st.title(plant.Name)
        st.snow()


def main(number_of_columns=3):
    columns = st.columns(number_of_columns)
    if 'plants' not in st.session_state:
        st.session_state['plants']: data.PowerPlants = data.get_power_plants()
    for i, plant in enumerate(st.session_state['plants'].root):
        with columns[i % number_of_columns]:
            with st.container():
                icon = ''
                if plant.type == 'WIND':
                    icon = ":blue[:material/wind_power:]"
                elif plant.type == 'SOLAR':
                    icon = ':orange[:material/sunny:]'
                else:
                    icon = ":material/question_mark:"
                st.title(icon + plant.name, anchor=False)
                st.subheader(f"Model: {plant.model}", anchor=False)
                st.link_button(f'Geolocation: {plant.geolocation.string}',
                               url=f"https://www.google.com/maps/place/"
                                   f"{plant.geolocation.latitude},{plant.geolocation.longitude}",
                               icon=":material/location_on:")
                st.button('See estimations', key=f'plant-{i}', icon=":material/wifi_channel:",
                          on_click=render_plant, args=(plant,))


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
