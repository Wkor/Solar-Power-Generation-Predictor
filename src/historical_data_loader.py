import pandas as pd
import requests as req
import datetime as dt
import time

class HistoricalDataLoader:
    def __init__(self, LATITUDE, LONGITUDE, START_DATE, END_DATE, SIGNS):
        self.LATITUDE = LATITUDE
        self.LONGITUDE = LONGITUDE
        self.START_DATE = START_DATE
        self.END_DATE = END_DATE
        self.SIGNS = SIGNS
        self.URL = "https://archive-api.open-meteo.com/v1/archive"
    
    def __get_chunk_per_date(self, start_date, end_date):
        params = {
            "latitude": self.LATITUDE,
            "longitude": self.LONGITUDE,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": ",".join(self.SIGNS)
        }   
    
        response = req.get(self.URL, params=params, timeout=30)
        data = response.json()
    
        dataframe = pd.DataFrame({'date': pd.to_datetime(data['hourly']['time'])})
        for param in self.SIGNS:
            dataframe[param] = data['hourly'][param]
    
        return dataframe

    def load_data(self, chunk_days=30):
        all_data = []
        current = self.START_DATE
        
        while current <= self.END_DATE:
            chunk_end = min(pd.to_datetime(current) + dt.timedelta(days=chunk_days - 1), self.END_DATE)
        
            chunk_df = self.__get_chunk_per_date(
                                       current.strftime('%Y-%m-%d'), 
                                       chunk_end.strftime('%Y-%m-%d'))
        
            if chunk_df is not None:
                all_data.append(chunk_df)
        
            current = chunk_end + dt.timedelta(days=1)
            time.sleep(0.5)
    
        return pd.concat(all_data, ignore_index=True)
        result = pd.read_csv('notebook/historical_weather.csv',index_col=False)
        print(result.head())
        result.drop(columns=['direct_normal_irradiance', 'direct_radiation', 'global_tilted_irradiance', 'shortwave_radiation', 'Unnamed: 0', 'surface_pressure', 'wind_speed_10m'],inplace=True)
        result['date'] = pd.to_datetime(result['date'])
        return result
