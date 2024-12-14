import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt


def analyze_city_temperature(city_data):
    city_df = city_data.copy()
    city_df['mean_temperature'] = city_df.groupby('season')['temperature'].transform('mean')
    city_df['std_temperature'] = city_df.groupby('season')['temperature'].transform('std')
    city_df['is_anomaly'] = (city_df['temperature'] < (city_df['mean_temperature'] - 2 * city_df['std_temperature'])) | (city_df['temperature'] > (city_df['mean_temperature'] + 2 * city_df['std_temperature']))
    return city_df


def get_current_weather_in_the_city(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()


st.title("Анализ температурных данных и мониторинг текущей температуры")

uploaded_file = st.file_uploader("Загрузите файл с историческими данными", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    cities = df['city'].unique()
    selected_city = st.selectbox("Выберите город", cities)

    city_data = df[df['city'] == selected_city]
    st.subheader(f"Описательная статистика для города {selected_city}")
    st.write(city_data['temperature'].describe())

    st.subheader("Временной ряд температур")
    plt.figure(figsize=(12, 6))
    plt.plot(city_data['timestamp'], city_data['temperature'], label='Температура', color='blue')
    plt.title(f"Температура в городе {selected_city}")
    plt.xlabel("Дата")
    plt.ylabel("Температура")
    plt.xticks([])

    city_data_res = analyze_city_temperature(city_data)
    anomalies = city_data_res[city_data_res['is_anomaly']]

    plt.scatter(anomalies['timestamp'], anomalies['temperature'], color='red', label='Аномалии для сезонов', zorder=5)

    plt.legend()
    st.pyplot(plt)

    city_season_mean_std = city_data.groupby('season')['temperature'].agg(['mean', 'std']).reset_index()

    st.subheader("Средняя температура и стандартное отклонение для сезонов")
    st.write(city_season_mean_std)

    api_key = st.text_input("Введите API-ключ для OpenWeatherMap", type="password")

    if api_key:
        weather = get_current_weather_in_the_city(selected_city, api_key)

        if weather.get("cod") != 200:
            st.error(weather.get("message", "Ошибка при получении данных"))
        else:
            city_current_temperature = weather['main']['temp']

            st.subheader(f"Текущая температура в городе {selected_city} {city_current_temperature}°C")

            seasons = ['winter', 'spring', 'summer', 'autumn']
            current_season = st.selectbox("Выберите текущий сезон", seasons)

            current_season_temperature_mean = city_season_mean_std[city_season_mean_std['season'] == current_season]['mean'].iloc[0]
            current_season_temperature_std = city_season_mean_std[city_season_mean_std['season'] == current_season]['std'].iloc[0]

            if (city_current_temperature < (current_season_temperature_mean - 2 * current_season_temperature_std)) or (city_current_temperature > (current_season_temperature_mean + 2 * current_season_temperature_std)):
                st.warning(f"Текущая температура аномальна для сезона {current_season}")
            else:
                st.success(f"Текущая температура нормальна для сезона {current_season}")
