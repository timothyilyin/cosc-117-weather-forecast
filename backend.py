import requests
from xml.etree import ElementTree as ET
from datetime import date, timedelta
from api_key import API_KEY
from config import CITY,WEATHER_EMOJI, POLLUTANTS, AQI_INTERVALS, INTERVAL_DESC

yesterday_string = (date.today()-timedelta(1)).strftime('%Y-%m-%d')
today_string = date.today().strftime('%Y-%m-%d')
tomorrow_string = (date.today()+ timedelta(1)).strftime('%Y-%m-%d')
day_after_tomorrow_string = (date.today()+ timedelta(2)).strftime('%Y-%m-%d')


def query_yesterday():
    return requests.get(f'https://api.weatherapi.com/v1/history.xml?key={API_KEY}&q={CITY}&dt={yesterday_string}')

def query_forecast():
    return requests.get(f'https://api.weatherapi.com/v1/forecast.xml?key={API_KEY}&q={CITY}&days=3&aqi=yes')

def process_day(day: ET.Element) -> tuple[str, str, str]:
    return day.find("condition/text").text, day.find("condition/code").text, day.find("avgtemp_c").text

def process_current(current: ET.Element) -> tuple[str, str, str, ET.Element]:
    return current.find("condition/text").text, current.find("condition/code").text, current.find("temp_c").text, current.find("air_quality")


def calc_aqi_level(concentration, intervals) -> str:
    for interval_level, interval_max in intervals:
        if float(concentration) <= interval_max:
            return interval_level
    return 7


def air_quality_summary(air_quality: ET.Element) -> str:
    qualities = {child.tag:child.text for child in air_quality}

    highest_level = 0
    highest_pollutant = ""
    highest_pollutant_concentration = 0
    num_missing = 0

    for pollutant in ["co", "no2", "so2", "pm2_5", "pm10", "o3"]:
        if pollutant in qualities:
            level = calc_aqi_level(qualities[pollutant], AQI_INTERVALS[pollutant])
            if  level > highest_level:
                highest_level = level
                highest_pollutant = pollutant
                highest_pollutant_concentration = qualities[pollutant]
        else:
            num_missing += 1

    if highest_level <= 2:
        return f"{INTERVAL_DESC[highest_level]}"
    else:
        return f"{INTERVAL_DESC[highest_level]} ({POLLUTANTS[highest_pollutant]}: {highest_pollutant_concentration})"




def get_four_day_weather():
    data = []
    yesterday = query_yesterday()
    if yesterday.status_code == 200:
        yesterday_element = ET.fromstring(yesterday.text).find("forecast/forecastday/day")
        yesterday_weather, yesterday_code,yesterday_temp = process_day(yesterday_element)
        data.append((yesterday_string, yesterday_weather, WEATHER_EMOJI[yesterday_code], yesterday_temp+" c"))
    forecast = query_forecast()
    if forecast.status_code == 200:
        forecast_root_element = ET.fromstring(forecast.text)
        current_element = forecast_root_element.find("current")
        current_weather, current_code, current_temp, current_air_quality = process_current(current_element)
        air_quality_str = air_quality_summary(current_air_quality)
        data.append((today_string, current_weather, WEATHER_EMOJI[current_code], current_temp+" c", air_quality_str))
     
        for forecastday_element in forecast_root_element.findall("forecast/forecastday"):
            if forecastday_element.find("date").text == tomorrow_string:
                tomorrow_element = forecastday_element.find("day")
                tomorrow_weather, tomorrow_code,tomorrow_temp = process_day(tomorrow_element)
                data.append((tomorrow_string, tomorrow_weather, WEATHER_EMOJI[tomorrow_code], tomorrow_temp+" c"))
        for forecastday_element in forecast_root_element.findall("forecast/forecastday"):
            if forecastday_element.find("date").text == day_after_tomorrow_string:
                day_after_tomorrow_element = forecastday_element.find("day")
                day_after_tomorrow_weather, day_after_tomorrow_code,day_after_tomorrow_temp = process_day(day_after_tomorrow_element)
                data.append((day_after_tomorrow_string, day_after_tomorrow_weather, WEATHER_EMOJI[day_after_tomorrow_code], day_after_tomorrow_temp+" c"))

    return data