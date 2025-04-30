#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import requests

# 🔹 Fixer API Key (Replace with your own valid API key)
FIXER_API_KEY = "c9a6a0eea7d55188922a356c473f3b10"

# 🔹 Function to Fetch Real-Time Exchange Rates
def get_exchange_rates(api_key, base_currency="EUR"):
    url = f"https://data.fixer.io/api/latest?access_key={api_key}&base={base_currency}"
    response = requests.get(url).json()
    
    if response.get("success"):
        return response["rates"]
    else:
        st.error(f"❌ Fixer API Error: {response.get('error', {}).get('info', 'Unknown error')}")
        return {}

# 🔹 Streamlit UI Setup
st.title("💱 Real-Time Currency Converter")
st.write("Convert currencies using live exchange rates.")

# 🔹 Sidebar Configuration
st.sidebar.header("Conversion Settings")

# Fetch exchange rates once
exchange_rates = get_exchange_rates(FIXER_API_KEY)

# If API failed, show error
if not exchange_rates:
    st.error("⚠️ Unable to fetch exchange rates. Please check your API key or try again later.")
else:
    currencies = list(exchange_rates.keys())  # Get available currency options

    # Select base and target currency
    base_currency = st.sidebar.selectbox("Select Base Currency", ["EUR"] + currencies)
    target_currency = st.sidebar.selectbox("Select Target Currency", currencies)

    # Input amount
    amount = st.sidebar.number_input("Enter Amount", min_value=0.01, value=1.00, step=0.01)

    # Convert currency
    if st.sidebar.button("Convert"):
        if target_currency in exchange_rates:
            converted_amount = round(amount * exchange_rates[target_currency], 2)
            st.success(f"💰 {amount} {base_currency} = {converted_amount} {target_currency}")
        else:
            st.error("⚠️ Unable to convert currency. Please check your selection.")


# In[ ]:




