# Save model and encoders to files
import joblib
import streamlit as st
from datetime import datetime

def load_model_and_predict(distance, surge_multiplier, rain, temp, humidity, clouds,
                          ride_name, cab_type, pickup_hour_counts, hour, day, wind, pressure):
    """
    Load saved model and encoders and make predictions
    
    Args:
        distance (float): Trip distance
        surge_multiplier (float): Surge multiplier
        rain (bool): Whether it's raining
        temp (float): Temperature
        humidity (int): Humidity percentage
        clouds (int): Cloud coverage percentage
        ride_name (str): Name of ride type
        cab_type (str): Type of cab
        pickup_hour_counts (int): Number of pickups in that hour
        hour (int): Hour of day
        day (int): Day of month
        wind (float): Wind speed
        pressure (float): Atmospheric pressure
        
    Returns:
        float: Predicted price
    """
    try:
        # Load model and encoders
        model = joblib.load('rf_model.joblib')
        cab_encoder = joblib.load('cab_type_encoder.joblib')
        ride_encoder = joblib.load('ride_name_encoder.joblib')
        
        # Encode categorical variables
        cab_type_encoded = cab_encoder.transform([cab_type])[0]
        ride_name_encoded = ride_encoder.transform([ride_name])[0]
        
        # Create feature array
        features = [[distance, cab_type_encoded, surge_multiplier, ride_name_encoded, temp, 
                    clouds, pressure, rain, humidity, wind, pickup_hour_counts, hour, day]]
        
        # Make prediction
        predicted_price = model.predict(features)[0]
        
        return predicted_price
    except FileNotFoundError:
        st.error("Required model files not found. Please ensure all model files are in the correct directory.")
        return None

def calculate_fare(distance, duration, booking_fee, base_fare, waiting_time_rate, distance_rate, minimum_fare,
                  surge_multiplier, rain, temp, humidity, clouds, wind, pressure, pickup_hour_counts,
                  temp_factor, humidity_factor, clouds_factor, wind_factor, pressure_factor, pickup_factor,
                  rain_factor):
    # Calculate base trip fare
    trip_fare = max(base_fare + (waiting_time_rate * duration) + (distance * distance_rate), minimum_fare)
    
    # Apply surge multiplier
    trip_fare *= surge_multiplier
    
    # Apply environmental factors
    if rain:
        trip_fare *= (1 + rain_factor)
    trip_fare *= (1 + (temp - 25) * temp_factor)  # Adjust based on deviation from 25°C
    trip_fare *= (1 + (humidity - 50) * humidity_factor)  # Adjust based on deviation from 50%
    trip_fare *= (1 + (clouds - 50) * clouds_factor)  # Adjust based on deviation from 50%
    trip_fare *= (1 + (wind - 10) * wind_factor)  # Adjust based on deviation from 10 mph
    trip_fare *= (1 + (pressure - 1013) * pressure_factor)  # Adjust based on deviation from 1013 hPa
    trip_fare *= (1 + (pickup_hour_counts - 50) * pickup_factor)  # Adjust based on deviation from 50 pickups
    
    # Add booking fee
    grand_total = trip_fare + booking_fee
    return round(grand_total, 2)

# Streamlit app
st.title('Cab Ride Price Predictor')

# Input fields
distance = st.number_input('Trip Distance (mil)', min_value=0.1, max_value=10.0, value=5.0)
surge_multiplier = st.number_input('Surge Multiplier', min_value=1.0, max_value=5.0, value=1.0)
rain = st.checkbox('Is it raining?')
temp = st.number_input('Temperature (°C)', min_value=-50.0, max_value=50.0, value=25.0)
humidity = st.slider('Humidity (%)', 0, 100, 50)
clouds = st.slider('Cloud Coverage (%)', 0, 100, 50)

try:
    ride_encoder = joblib.load('ride_name_encoder.joblib')
    ride_name = st.selectbox('Ride Type', ride_encoder.classes_)
except FileNotFoundError:
    st.error("Ride encoder file not found. Please ensure ride_name_encoder.joblib is in the correct directory.")
    ride_name = None

cab_type = st.selectbox('Cab Type', ['Uber', 'Lyft'])
wind = st.number_input('Wind Speed (mph)', min_value=0.0, max_value=100.0, value=10.0)
pressure = st.number_input('Atmospheric Pressure (hPa)', min_value=900.0, max_value=1100.0, value=1013.0)

# Time inputs
hour = st.number_input('Hour of Day', min_value=0, max_value=24, value=datetime.now().hour)
day = st.number_input('Day of Month', min_value=1, max_value=31, value=datetime.now().day)
pickup_hour_counts = st.number_input('Number of Pickups in Hour', min_value=0, max_value=100000, value=50)

if st.button('Predict Price'):
    if ride_name is not None:
        price = load_model_and_predict(distance, surge_multiplier, rain, temp, humidity, clouds,
                                     ride_name, cab_type, pickup_hour_counts, hour, day, wind, pressure)
        if price is not None:
            st.success(f'Predicted Price: ${price:.2f}')

# Voo's Current Calculation Section
st.title("_____________________________")
st.title("Voo's Current Fare Calculator")

# Trip Details
st.subheader("Trip Details")
distance_voo = st.number_input('Trip Distance for Voo (mil)', min_value=0.1, max_value=1000.0, value=5.0, key='distance_voo')
duration_voo = st.number_input('Trip Duration (minutes)', min_value=1, max_value=120, value=15)
pickup_hour_counts_voo = st.number_input('Number of Pickups in Hour', min_value=0, max_value=100000, value=50, key='pickup_voo')
rain_voo = st.checkbox('Is it raining?', key='rain_voo')
temp_voo = st.number_input('Temperature (°C)', min_value=-50.0, max_value=50.0, value=25.0, key='temp_voo')
humidity_voo = st.slider('Humidity (%)', 0, 100, 50, key='humidity_voo')
clouds_voo = st.slider('Cloud Coverage (%)', 0, 100, 50, key='clouds_voo')
wind_voo = st.number_input('Wind Speed (mph)', min_value=0.0, max_value=100.0, value=10.0, key='wind_voo')
pressure_voo = st.number_input('Atmospheric Pressure (hPa)', min_value=900.0, max_value=1100.0, value=1013.0, key='pressure_voo')
# Environmental Factors
# Base Fare Components
st.subheader("Base Fare Components")
surge_multiplier_voo = st.number_input('Surge Multiplier', min_value=1.0, max_value=5.0, value=1.0, key='surge_voo')
pickup_factor = st.number_input('Pickup Count /h factor', min_value=-1.0, max_value=0.23, value=0.0005, step=0.0001)
booking_fee = st.number_input('Booking Fee ($)', min_value=0.0, value=2.02, step=0.01)
base_fare = st.number_input('Base Fare ($)', min_value=0.0, value=2.45, step=0.01)
waiting_time_rate = st.number_input('charges ($/minute)', min_value=0.0, value=0.17, step=0.01)
distance_rate = st.number_input('charges ($/mile)', min_value=0.0, value=0.73, step=0.01)
minimum_fare = st.number_input('Minimum Fare ($)', min_value=0.0, value=5.0, step=0.01)

# Factor Adjustment Rates
st.subheader("Factor Adjustment Rates")
temp_factor = st.number_input('Temperature Factor', min_value=-1.0, max_value=0.1, value=0.024, step=0.001)
humidity_factor = st.number_input('Humidity Factor', min_value=-1.0, max_value=0.1, value=0.011, step=0.001)
clouds_factor = st.number_input('Cloud Coverage Factor', min_value=-1.0, max_value=0.1, value=0.02, step=0.001)
wind_factor = st.number_input('Wind Speed Factor', min_value=-1.0, max_value=0.1, value=0.013, step=0.001)
pressure_factor = st.number_input('Pressure Factor', min_value=-1.0, max_value=0.1, value=-0.022, step=0.001)

rain_factor = st.number_input('Rain Factor', min_value=-1.0, max_value=1.0, value=-0.017, step=0.01)

if st.button('Calculate Voo Fare'):
    voo_price = calculate_fare(
        distance_voo, duration_voo, booking_fee, base_fare, waiting_time_rate, distance_rate, minimum_fare,
        surge_multiplier_voo, rain_voo, temp_voo, humidity_voo, clouds_voo, wind_voo, pressure_voo,
        pickup_hour_counts_voo, temp_factor, humidity_factor, clouds_factor, wind_factor, pressure_factor,
        pickup_factor, rain_factor
    )
    st.success(f"Voo's Current Fare: ${voo_price:.2f}")
