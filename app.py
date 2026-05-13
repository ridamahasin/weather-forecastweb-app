from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)

weather_conditions = {
    0: ("Clear Sky", "☀️", "sunny"),
    1: ("Mainly Clear", "🌤️", "sunny"),
    2: ("Partly Cloudy", "⛅", "cloudy"),
    3: ("Cloudy", "☁️", "cloudy"),
    45: ("Fog", "🌫️", "fog"),
    48: ("Fog", "🌫️", "fog"),
    51: ("Light Drizzle", "🌦️", "rainy"),
    61: ("Rain", "🌧️", "rainy"),
    63: ("Moderate Rain", "🌧️", "rainy"),
    65: ("Heavy Rain", "⛈️", "rainy"),
    71: ("Snow", "❄️", "snow"),
    95: ("Thunderstorm", "⛈️", "storm")
}

@app.route('/', methods=['GET', 'POST'])
def home():

    weather = None
    error = None
    forecast = []
    background = "default"
    suggestion = ""

    current_time = datetime.now().strftime("%d %B %Y | %I:%M %p")

    if request.method == 'POST':

        city = request.form['city']

        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"

        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()

        if 'results' in geo_data:

            latitude = geo_data['results'][0]['latitude']
            longitude = geo_data['results'][0]['longitude']
            city_name = geo_data['results'][0]['name']
            country = geo_data['results'][0]['country']

            weather_url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={latitude}&longitude={longitude}"
                f"&current=temperature_2m,relative_humidity_2m,"
                f"apparent_temperature,wind_speed_10m,weather_code"
                f"&daily=temperature_2m_max,temperature_2m_min,weather_code"
                f"&timezone=auto"
            )

            response = requests.get(weather_url)
            data = response.json()

            code = data['current']['weather_code']

            condition, icon, background = weather_conditions.get(
                code,
                ("Unknown", "🌍", "default")
            )

            weather = {
                'city': city_name,
                'country': country,
                'temperature': data['current']['temperature_2m'],
                'humidity': data['current']['relative_humidity_2m'],
                'feels_like': data['current']['apparent_temperature'],
                'wind': data['current']['wind_speed_10m'],
                'condition': condition,
                'icon': icon
            }

            if weather['temperature'] > 35:
                suggestion = "🥤 Stay hydrated and avoid too much sunlight"

            elif "Rain" in weather['condition']:
                suggestion = "☔ Carry an umbrella today"

            elif weather['temperature'] < 15:
                suggestion = "🧥 Wear warm clothes outside"

            else:
                suggestion = "🌤️ Weather looks pleasant today"

            dates = data['daily']['time']
            max_temp = data['daily']['temperature_2m_max']
            min_temp = data['daily']['temperature_2m_min']
            codes = data['daily']['weather_code']

            for i in range(5):

                forecast_condition, forecast_icon, _ = weather_conditions.get(
                    codes[i],
                    ("Unknown", "🌍", "default")
                )

                forecast.append({
                    'date': dates[i],
                    'max': max_temp[i],
                    'min': min_temp[i],
                    'icon': forecast_icon,
                    'condition': forecast_condition
                })

        else:
            error = "City not found"

    return render_template(
        'index.html',
        weather=weather,
        error=error,
        forecast=forecast,
        background=background,
        current_time=current_time,
        suggestion=suggestion
    )

if __name__ == '__main__':
    app.run(debug=True)