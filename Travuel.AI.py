import subprocess
import sys

# Function to install missing packages
def install_and_import(packages):
    for package_name, import_name in packages.items():
        try:
            __import__(import_name)
        except ImportError:
            print(f"📦 Installing missing package: {package_name}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            globals()[import_name] = __import__(import_name) 

# Mapping of required packages
required_packages = {
    "streamlit": "streamlit",
    "requests": "requests",
    "googlemaps": "googlemaps",
    "folium": "folium",
    "openai": "openai",
    "streamlit-folium": "streamlit_folium",
    "pandas": "pandas",
    "pinecone-client": "pinecone",
}

# Install and import packages
install_and_import(required_packages)

# Now safely import all packages
import streamlit as st
import requests
import googlemaps  # Ensure googlemaps is available
import folium
from openai import OpenAI
from streamlit_folium import st_folium
import pandas as pd
from io import BytesIO
from pinecone import Pinecone
import re

# API Keys (Replace with actual keys)
FIXER_API_KEY = "b76c3f0667d5e880a2e40cac232b9c0b"
GOOGLE_MAPS_API_KEY = "AIzaSyBNelRNmB2AmbH8E_29bs1MA-KFQL2LnSo"
WEATHER_API_KEY = "8a0013e5d23e41d08df224236253101"
OPENAI_API_KEY = "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"
PINECONE_API_KEY = "pcsk_7FSrbr_5ZXTGbjRENDPSbGMEQM7i9FPk9YmB9heXjCYStjjM1UnDC88eLqoc2cA9sZYszS"

# Initialize Google Maps API Client
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# Cache for location coordinates
location_coords_cache = {}

# Set background color to Tiffany Blue and text color to White
st.markdown(
    """
    <style>
    body {
        background-color: #0ABAB5 !important; /* Tiffany Blue Background */
        font-family: 'Sans-serif' !important;
        color: #FFFFFF !important; /* Unified Text Color to White */
    }
    
    /* Ensure markdown section has a white background with black text */
    .markdown-box {
        background-color: #FFFFFF !important; /* White Background */
        color: #000000 !important; /* Black Text */
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        font-size: 25px !important; /* Ensure Font Size Consistency */
    }

    .stDataFrame {
        font-size: 25px !important; /* Ensure Font Size in DataFrames */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit UI
st.markdown('<h1>🌍 Welcome to Travuel.AI <br> Your Personal Travel Guide ✈️</h1>', unsafe_allow_html=True)

# Information Box with White Background and Black Text
st.markdown(
    """
    <div class="markdown-box">
    
    <strong>To get the most accurate and personalized travel recommendations, try asking questions like:</strong>
    
    <br>
    <strong>✔ Hidden Gems & Local Experiences</strong>  
    👉 <em>"What are some hidden gems and off-the-beaten-path experiences?"</em>  
    <br><small>(Discover secret spots, unique cultural sites, and local favorites.)</small>

    <br>
    <strong>✔ Best Restaurants & Nightlife</strong>  
    👉 <em>"What are the best restaurants and nightspots in San Francisco for an unforgettable experience?"</em>  
    <br><small>(Get top dining, rooftop bars, and nightlife recommendations.)</small>

    <br>
    <strong>✔ Events & Seasonal Attractions</strong>  
    👉 <em>"What must-see events and seasonal attractions are happening in San Francisco this month?"</em>  
    <br><small>(Stay updated on festivals, concerts, and seasonal highlights.)</small>

    <br>
    <strong>💡 Tip:</strong> Be specific! Mention your <strong>preferences, budget, or travel dates</strong> for even better recommendations.
    
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("Travuel.AI")



# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("guide")

# Initialize session state
st.session_state.setdefault("recommendations", [])
st.session_state.setdefault("summary", "")
st.session_state.setdefault("weather_data", "")
st.session_state.setdefault("city", "San Francisco")
st.session_state.setdefault("temperature_unit", "C")





# User enters travel query
query = st.text_input("Now, it is your time to experience the power of generative AI!")


# Function to dynamically extract city name, ensuring proper multi-word city capture
def extract_city_name(query):
    match = re.search(r"in\s+([\w\s]+?)(?=\s+(?:this|next|last|on|at|by|for|from|to|until|before|after|month|week|day|year|night|morning|afternoon|evening|today|tomorrow|yesterday|now|soon|later|ahead|coming|going|departing|returning|visiting|exploring|staying|traveling|checking|looking)\b|$)", query, re.IGNORECASE)
    return match.group(1).strip() if match else "San Francisco"

# Extract city name dynamically from user query
st.session_state.city = extract_city_name(query)

def get_real_time_travel_time(origin, destination, mode="driving"):
        try:
            result = gmaps.distance_matrix(origins=[origin], destinations=[destination], mode=mode)
            if result['rows'][0]['elements'][0]['status'] == "OK":
                travel_time = result['rows'][0]['elements'][0]['duration']['value'] / 60  # Convert seconds to minutes
                return travel_time
            else:
                st.error(f"Error: {result['rows'][0]['elements'][0]['status']} for {origin} to {destination}")
                return None
        except Exception as e:
            st.error(f"Error fetching travel time for {origin} to {destination}: {e}")
            return None
# Function to get latitude and longitude for locations
def get_lat_lon(location):
        if location in location_coords_cache:
            return location_coords_cache[location]

        try:
            geocode_result = gmaps.geocode(location + ", San Francisco")
            if geocode_result:
                lat = geocode_result[0]['geometry']['location']['lat']
                lon = geocode_result[0]['geometry']['location']['lng']
                location_coords_cache[location] = (lat, lon)
                return lat, lon
        except Exception as e:
            st.error(f"Error fetching coordinates for {location}: {e}")
            return None, None
def add_route_with_transportation_mode(route, map_obj, mode="driving"):
        for i in range(len(route) - 1):
            origin = route[i] + ", San Francisco"
            destination = route[i + 1] + ", San Francisco"

            # Fetch travel time based on the transportation mode
            travel_time = get_real_time_travel_time(origin, destination, mode=mode)
            if travel_time:
                # Get coordinates
                origin_coords = location_coords_cache.get(route[i])
                destination_coords = location_coords_cache.get(route[i + 1])

                if origin_coords and destination_coords:
                    # Choose a line color based on the transportation mode
                    color = "blue" if mode == "driving" else "green" if mode == "walking" else "purple"

                    # Add a line to the map
                    folium.PolyLine(
                        locations=[origin_coords, destination_coords],
                        color=color,
                        weight=3,
                        opacity=0.8,
                    ).add_to(map_obj)

                    # Add a travel time label
                    midpoint = [
                        (origin_coords[0] + destination_coords[0]) / 2,
                        (origin_coords[1] + destination_coords[1]) / 2,
                    ]
                    folium.Marker(
                        location=midpoint,
                        icon=folium.DivIcon(html=f"""
                            <div style="
                                font-size: 12px;
                                font-weight: bold;
                                color: black;
                                background-color: white;
                                border: 1px solid black;
                                padding: 10px;
                                border-radius: 8px;
                                min-width: 40px;
                                text-align: center;
                            ">
                                {int(travel_time)} min
                            </div>
                        """),
                    ).add_to(map_obj)

# Function to generate the map based on user inputs
def generate_map(locations, transport_mode):
    if not locations:
        st.error("Please enter at least two locations.")
        return None

     # Split and clean user input into a list of locations
    locations = [loc.strip() for loc in locations if loc.strip()]

    if len(locations) < 2:
        st.error("You need at least two locations for an optimized route.")
        return None

    # Fetch and store coordinates
    for loc in locations:
        get_lat_lon(loc)

    # Create a folium map centered around San Francisco
    sf_map = folium.Map(location=[37.7749, -122.4194], zoom_start=13)


    # Add route with the selected transportation mode
    add_route_with_transportation_mode(locations, sf_map, mode=transport_mode)

    # Add markers for each stop
    for loc in locations:
        lat_lon = location_coords_cache.get(loc)
        if lat_lon:
            folium.Marker(
                location=lat_lon,
                popup=f"<b>{loc}</b>",
                tooltip=loc,
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(sf_map)

    # Return the map object for visualization and download
    return sf_map


# Function to convert temperature
def convert_temp(celsius, unit):
    return celsius if unit == "C" else (celsius * 9/5) + 32

# Function to generate embeddings using OpenAI
def get_embedding(text):
    response = OpenAI(api_key=OPENAI_API_KEY).embeddings.create(
        model="text-embedding-ada-002",
        input=[text]  # Should be a list
    )
    return response.data[0].embedding

# Function to dynamically extract relevant metadata
def extract_metadata(matches):
    extracted_info = []
    names = []
    locations = []

    for match in matches:
        metadata = match.get("metadata", {})
        guide_type = metadata.get("guide_type", "").lower()

        # Extract name dynamically based on guide type
        name_key = next((key for key in metadata.keys() if "name" in key.lower()), None)
        name = metadata.get(name_key, "Unknown") if name_key else "Unknown"
        if name != "Unknown" and name not in names:
            names.append(name)

        # Extract location only if guide_type is "events"
        location_key = next((key for key in metadata.keys() if "location" in key.lower()), None)
        location = metadata.get(location_key, "Unknown") if location_key and guide_type == "events" else None
        if location and location != "Unknown" and location not in locations:
            locations.append(location)

        # Dynamically collect other metadata fields
        details = {key: value for key, value in metadata.items() if key not in ["guide_type", name_key, location_key]}

        extracted_info.append({
            "name": name,
            "type": guide_type.capitalize(),
            "details": details,
            "location": location if guide_type == "events" else None,
        })

    return extracted_info, names, locations

# Function to generate travel recommendations dynamically
def generate_travel_recommendations(query):
    query_embedding = get_embedding(query)
    search_results = index.query(
        vector=query_embedding,
        top_k=10,
        include_metadata=True
    )

    extracted_info, place_names, event_locations = extract_metadata(search_results["matches"])

    # Generate structured output for OpenAI
    structured_data = "\n\n".join(
        f"📍 {info['name']} ({info['type']})\n"
        + "\n".join([f"- **{key.replace('_', ' ').capitalize()}**: {value}" for key, value in info["details"].items()])
        for info in extracted_info
    )

    if structured_data:
        prompt = f"Based on the following travel-related data, generate a structured travel guide:\n\n{structured_data}\n\nUser Query: {query}"
    else:
        prompt = f"No relevant travel information found. Still try to answer based on general knowledge. User Query: {query}"

    response = OpenAI(api_key=OPENAI_API_KEY).chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a travel guide assistant providing detailed recommendations."}, 
                  {"role": "user", "content": prompt}]
    )

    llm_response = response.choices[0].message.content.strip()
    return llm_response, place_names, event_locations

# Button to trigger processing
if st.button("Make My Travel Easier!"):
    llm_summary, place_names, event_locations = generate_travel_recommendations(query)

    # Preserve previous recommendations if new ones are found
    if place_names:
        st.session_state.recommendations = place_names
    elif not st.session_state.recommendations:
        st.error("No valid recommendations found. Please try another query.")
    
    st.session_state.summary = llm_summary

    # Fetch weather data
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={st.session_state.city}&days=7&aqi=no&alerts=no"
    response = requests.get(url).json()
    st.session_state.weather_data = response.get("forecast", {}).get("forecastday", [])

# Display recommendations
if st.session_state.recommendations:
    st.subheader("✈️ Recommended Travel Spots")
    st.write(st.session_state.summary)


# Display weather forecast
if st.session_state.weather_data:
    weather_df = pd.DataFrame([
        {
            "Max Temp (°C)": convert_temp(day["day"]["maxtemp_c"], "C"),
            "Min Temp (°C)": convert_temp(day["day"]["mintemp_c"], "C"),
            "Max Temp (°F)": convert_temp(day["day"]["maxtemp_c"], "F"),
            "Min Temp (°F)": convert_temp(day["day"]["mintemp_c"], "F"),
            "Condition": day["day"]["condition"]["text"]
        }
        for day in st.session_state.weather_data
    ], index=[day["date"] for day in st.session_state.weather_data])  # Set Date as index

    st.subheader(f"🌦️ 7-Day Weather Forecast for {st.session_state.city}")
    st.dataframe(weather_df)











#Function to get latitude and longitude for event locations
def get_lat_lon(location):
    if location in location_coords_cache:
        return location_coords_cache[location]

    try:
        geocode_result = gmaps.geocode(location)
        if geocode_result:
            lat = geocode_result[0]['geometry']['location']['lat']
            lon = geocode_result[0]['geometry']['location']['lng']
            location_coords_cache[location] = (lat, lon)
            return lat, lon
    except Exception:
        return None, None



selected_places = st.multiselect(
    "Select places to include in your itinerary",
    st.session_state.recommendations,
    default=st.session_state.recommendations
)

transport_mode = st.radio(
    "Select Transportation Mode",
    options=["driving", "walking", "bicycling", "transit"],
    index=0
)

if selected_places:
    sf_map = generate_map(selected_places, transport_mode)
    st_folium(sf_map, width=700, height=500)












# Currency Conversion - Fetch live exchange rates
def get_exchange_rate(currency):
    url = f"https://data.fixer.io/api/latest?access_key={FIXER_API_KEY}"
    response = requests.get(url).json()
    return response.get("rates", {}).get(currency, 1)

# Currency Conversion - Sidebar Configuration
st.sidebar.header("💱 Currency Converter")

# Function to fetch real-time exchange rates
def get_exchange_rates(api_key, base_currency="EUR"):
    url = f"https://data.fixer.io/api/latest?access_key={api_key}&base={base_currency}"
    response = requests.get(url).json()
    
    if response.get("success"):
        return response["rates"]
    else:
        st.sidebar.error(f"❌ Fixer API Error: {response.get('error', {}).get('info', 'Unknown error')}")
        return {}

# Fetch exchange rates once
exchange_rates = get_exchange_rates(FIXER_API_KEY)

if exchange_rates:
    currencies = list(exchange_rates.keys())

    # Select base and target currency
    base_currency = st.sidebar.selectbox("Select Base Currency", ["EUR"] + currencies)
    amount = st.sidebar.number_input(f"Enter Amount in {base_currency}", min_value=0.0, value=1.0, step=0.1)
    target_currency = st.sidebar.selectbox("Select Target Currency", currencies)
    
    # Button to trigger conversion
    if st.sidebar.button("Check Rate"):
        if base_currency in exchange_rates and target_currency in exchange_rates:
            conversion_rate = exchange_rates[target_currency] / exchange_rates[base_currency]
            converted_amount = round(amount * conversion_rate, 2)
            
            # Display conversion rate and result
            st.sidebar.info(f"💲 {amount} {base_currency} = {converted_amount} {target_currency}")
        else:
            st.sidebar.error("⚠️ Unable to fetch exchange rate. Please check your selection.")