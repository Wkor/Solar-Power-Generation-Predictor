import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
import datetime as dt

class ForecastedDataLoader:
    def __init__(self, SIGNS, START_DATE, END_DATE, LATITUDE, LONGITUDE):
        self.SIGNS = SIGNS
        self.START_DATE = START_DATE
        self.END_DATE = END_DATE
        self.LATITUDE = LATITUDE
        self.LONGITUDE = LONGITUDE
        self.URL = "https://api.open-meteo.com/v1/forecast"

        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)
        
    def load_data(self):
        start_dt = dt.date.strptime(self.START_DATE, '%Y-%m-%d')
        end_dt = dt.date.strptime(self.END_DATE, '%Y-%m-%d')
        days = (end_dt - start_dt).days + 1
    
        params = {
            "latitude": self.LATITUDE,
            "longitude": self.LONGITUDE,
            "hourly": ",".join(self.SIGNS),
            "forecast_days": days
        }

        responses = self.openmeteo.weather_api(self.URL, params=params)

        response = responses[0]

        hourly = response.Hourly()

        hourly_data = {"date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )}
        
        for i, param in enumerate(self.SIGNS):
            hourly_data[param] = hourly.Variables(i).ValuesAsNumpy()
        
        df = pd.DataFrame(data=hourly_data)
        
        return df