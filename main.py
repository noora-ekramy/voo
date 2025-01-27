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
def calculate_fare(distance, duration):
    # Constants
    booking_fee = 2.02
    base_fare = 2.45
    waiting_time_rate = 0.17
    distance_rate = 0.73
 
    tax_rate = 0.062
    extra_charge_rate = 0.06
    minimum_fare = 5.0

    
    trip_fare = max(base_fare + (waiting_time_rate * duration) + (distance * distance_rate) , minimum_fare)
    grand_total = trip_fare + booking_fee

    return round(grand_total, 2)
# Streamlit app
st.title('Cab Ride Price Predictor')

# Input fields
distance = st.number_input('Trip Distance (km)', min_value=0.1, max_value=10.0, value=5.0)
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
wind = st.number_input('Wind Speed (km/h)', min_value=0.0, max_value=100.0, value=10.0)
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
st.title("Voo's Current Fare Calculator")
distance_voo = st.number_input('Trip Distance for Voo (km)', min_value=0.1, max_value=10.0, value=5.0, key='distance_voo')
duration_voo = st.number_input('Trip Duration (minutes)', min_value=1, max_value=120, value=15)

if st.button('Calculate Voo Fare'):
    voo_price = calculate_fare(distance_voo, duration_voo)
    st.success(f"Voo's Current Fare: ${voo_price:.2f}")
