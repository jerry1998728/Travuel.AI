# 🌍 Travuel.AI — Your Generative AI Travel Assistant ✈️

Travuel.AI is an interactive travel planning chatbot that combines LLM-powered recommendations with real-time external APIs to deliver a personalized, visual, and information-rich travel experience. Built using Streamlit, it lets users explore destinations, view custom travel routes, analyze weather, and convert currencies—all in one unified web-based application.

---

## Features

### ✨ 1. Generative Travel Recommendations (via OpenAI + Pinecone Knowledge Base)
- Ask natural language questions like:
  - “What are hidden gems in San Francisco?”
  - “Top events and restaurants happening next weekend?”
- Uses OpenAI GPT-4o + Pinecone semantic search to:
  - Find updated top attractions, events, and local food spots
  - Extract structured metadata (names, types, descriptions)
  - Return a natural, personalized response

### 🗺️ 2. Smart Itinerary & Route Planner (Powered by Google Maps + Folium)
- Input the places you want to visit → see optimized routes
- Select transportation mode (driving, walking, transit, biking)
- Auto-calculates travel time between stops
- Visualizes routes on a fully interactive map

### 🌦️ 3. 7-Day Weather Forecast (Powered by WeatherAPI)
- Auto-detects city from your query
- Displays temperature (°C & °F) and weather conditions
- Uses real-time data from [weatherapi.com](https://www.weatherapi.com)

### 💱 4. Live Currency Conversion (Powered by Fixer.io)
- Sidebar tool for checking real-time exchange rates
- Converts between EUR, USD, GBP, and more

---

## Tech Stack

| Tech       | Purpose                              |
|------------|---------------------------------------|
| **Streamlit** | Frontend UI & interactivity       |
| **OpenAI GPT-4o** | Generative text responses     |
| **Pinecone** | Semantic search & vector retrieval |
| **Google Maps API** | Geocoding, distance matrix |
| **Folium** | Route & map visualization            |
| **WeatherAPI** | Real-time forecast data          |
| **Fixer.io** | Currency conversion                |

---

Built by Santa Clara University MSBA students: Jerry Hsieh, Luara Cheng, Kelly Xie, Simon Zheng
