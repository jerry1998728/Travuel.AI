import streamlit as st
import requests
import pandas as pd

# Hardcoded API Key (Replace with your own key)
API_KEY = "8a0013e5d23e41d08df224236253101"

# Function to get weather forecast
def get_weather_forecast(location="San Francisco", days=3):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={location}&days={days}&aqi=no&alerts=no"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Unable to fetch weather data"}

# Streamlit UI
st.title("San Francisco Weather Forecast App")

# Remove API Key input field
# st.text_input("Enter your Weather API Key:")  # DELETE this line

# Remove unnecessary input for city name since it's fixed
# st.text_input("Enter City Name:", "San Francisco")  # DELETE this line

# User selects the number of forecast days
days = st.slider("Select Number of Days for Forecast", min_value=1, max_value=7, value=3)

# Fetch weather forecast
weather_forecast = get_weather_forecast(days=days)

if "forecast" in weather_forecast:
    forecast_data = []
    for day in weather_forecast["forecast"]["forecastday"]:
        forecast_data.append({
            "Date": day["date"],
            "Avg Temperature (°C)": day["day"]["avgtemp_c"],
            "Max Temperature (°C)": day["day"]["maxtemp_c"],
            "Min Temperature (°C)": day["day"]["mintemp_c"],
            "Condition": day["day"]["condition"]["text"],
            "Wind Speed (kph)": day["day"]["maxwind_kph"],
            "Humidity (%)": day["day"]["avghumidity"],
            "Precipitation (mm)": day["day"]["totalprecip_mm"],
            "UV Index": day["day"]["uv"]
        })

    # Convert to DataFrame and display
    df = pd.DataFrame(forecast_data)
    st.dataframe(df)

else:
    st.error("Failed to retrieve weather data. Please check your API key or try again later.")
