import streamlit as st
import googlemaps
import folium
from streamlit_folium import st_folium
from io import BytesIO

#Set up Google Maps API client
GOOGLE_MAPS_API_KEY = "placeholder"
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

#Cache for location coordinates
location_coords_cache = {}

#Function to get real-time travel time
def get_real_time_travel_time(origin, destination, mode="driving"):
    """
    Fetches real-time travel time between two locations using Google Maps API.
    """
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

#Function to get latitude and longitude for locations
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

#Function to add categorized markers
def add_categorized_markers(route, map_obj):
    categories = {
        "Golden Gate Park": "Outdoor Activities",
        "El Rio": "Night Activities",
        "Twin Peaks": "SF Culture",
        "DNA Lounge": "Night Activities",
        "Ferry Plaza Farmers Market": "Restaurant"
    }

    for location in route:
        coords = location_coords_cache.get(location)
        if coords:
            category = categories.get(location, "General")
            color = (
                "blue" if category == "SF Culture" else
                "green" if category == "Outdoor Activities" else
                "purple" if category == "Night Activities" else
                "orange" if category == "Restaurant" else
                "red"
            )

            folium.Marker(
                location=coords,
                popup=f"<b>{location}</b><br>Category: {category}",
                icon=folium.Icon(color=color, icon="info-sign"),
            ).add_to(map_obj)

#Function to add routes with travel times
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

#Function to generate the map based on user inputs
def generate_map(locations, transport_mode):
    if not locations:
        st.error("Please enter at least two locations.")
        return None

    #Split and clean user input into a list of locations
    locations = [loc.strip() for loc in locations.split(",") if loc.strip()]

    if len(locations) < 2:
        st.error("You need at least two locations for an optimized route.")
        return None

    #Fetch and store coordinates
    for loc in locations:
        get_lat_lon(loc)

    #Create a folium map centered around San Francisco
    sf_map = folium.Map(location=[37.7749, -122.4194], zoom_start=13)

    #Add categorized markers for all stops
    add_categorized_markers(locations, sf_map)

    #Add route with the selected transportation mode
    add_route_with_transportation_mode(locations, sf_map, mode=transport_mode)

    #Return the map object for visualization and download
    return sf_map

#Streamlit App
st.title("🚗 San Francisco Route Planner")
st.write("Enter locations and choose your preferred transportation mode to generate an optimized route.")

#Input fields
locations_input = st.text_input("Enter locations (comma-separated)", "Golden Gate Park, El Rio, Twin Peaks, DNA Lounge, Ferry Plaza Farmers Market")
transport_mode = st.selectbox("Choose Transportation Mode", ["driving", "walking", "transit"])

if st.button("Generate Route"):
    # Generate the map and store it in session state
    sf_map = generate_map(locations_input, transport_mode)

    if sf_map:
        # Cache the map object
        st.session_state["sf_map"] = sf_map

#Render the map only if it's cached
if "sf_map" in st.session_state:
    sf_map = st.session_state["sf_map"]

    # Display the map
    st_folium(sf_map, width=700, height=500)

    # Save the map to a buffer for downloading
    map_buffer = BytesIO()
    sf_map.save(map_buffer, close_file=False)

    # Add a download button
    st.download_button(
        label="Download Map as HTML",
        data=map_buffer.getvalue(),
        file_name="san_francisco_route_map.html",
        mime="text/html"
    )
