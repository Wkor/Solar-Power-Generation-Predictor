import pandas as pd
import numpy as np 
import datetime as dt

class DataProcessor:
    def __init__(self, production_data, historical_weather, forecasted_weather, SIGNS, DAYS, ID_STATION):
        self.production_data = production_data
        self.historical_weather = historical_weather
        self.SIGNS = SIGNS
        self.forecasted_weather = forecasted_weather
        self.DAYS = DAYS
        self.ID_STATION = ID_STATION

    
    def merged_meteo_and_prod(self):
        meteo_and_prod = pd.merge( 
        self.historical_weather,
        self.production_data,
        on='date',
        how='left',
    )

        sum_columns = ['diffuse_radiation', 'terrestrial_radiation'] 
        mean_columns = ['cloud_cover', 'relative_humidity_2m', 'temperature_2m', 'wind_speed_10m', 'surface_pressure'] 

        for col in meteo_and_prod.columns:
            if col not in ['id_station', 'date', 'production']:
                if col in mean_columns and pd.api.types.is_numeric_dtype(meteo_and_prod[col]):
                    mean_columns.append(col) if col not in mean_columns else None
                elif pd.api.types.is_numeric_dtype(meteo_and_prod[col]):
                    sum_columns.append(col)
    
        agg_dict = {}
        for col in sum_columns:
            agg_dict[col] = 'sum'
        for col in mean_columns:
            if col in meteo_and_prod.columns and pd.api.types.is_numeric_dtype(meteo_and_prod[col]):
                agg_dict[col] = 'mean'
        if 'production' in meteo_and_prod.columns:
            agg_dict['production'] = 'first'
        meteo_and_prod = (
            meteo_and_prod.groupby(['id_station', 'date'])
            .agg(agg_dict)
            .reset_index()
        )

        return meteo_and_prod
    
    def delete_anomalies(self, dataframe, subset_column):
        q1 = dataframe[subset_column].quantile(0.25) 
        q3 = dataframe[subset_column].quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr 
        upper_bound = q3 + 1.5 * iqr

        dataframe.loc[(dataframe[subset_column] < lower_bound) | (dataframe[subset_column] > upper_bound), subset_column] = np.nan
        
    def process_forecasted_data(self):
        self.forecasted_weather['date'] = pd.to_datetime(self.forecasted_weather['date']).dt.normalize()

        sum_cols = ['diffuse_radiation', 'terrestrial_radiation', 'shortwave_radiation', 'direct_radiation']
        
        agg_dict = {}
        for col in self.forecasted_weather.columns:
            if col in ['date', 'id_station']:
                continue
            
            if col in sum_cols:
                agg_dict[col] = 'sum'
            else:
                if pd.api.types.is_numeric_dtype(self.forecasted_weather[col]):
                    agg_dict[col] = 'mean'

        daily_historical = self.forecasted_weather.groupby(['date', 'id_station']).agg(agg_dict).reset_index()
        
        return daily_historical


    
    def process_data(self):    
        self.production_data['production'] = pd.to_numeric(self.production_data['production'], errors='coerce')
        self.historical_weather["date"] = pd.to_datetime(self.historical_weather['date']).dt.date
        self.production_data["date"] = pd.to_datetime(self.production_data["date"]).dt.date
        self.forecasted_weather["date"] = pd.to_datetime(self.forecasted_weather['date'], errors='coerce').dt.date
        
        self.forecasted_weather['id_station'] = self.ID_STATION
        meteo_and_prod = self.merged_meteo_and_prod()
        meteo_and_prod.sort_values(by='date', inplace=True)
        self.delete_anomalies(meteo_and_prod, 'production')
        meteo_and_prod.dropna(inplace=True)
        meteo_and_prod.drop_duplicates(subset=['date','id_station'], keep='first', inplace=True)
        self.forecasted_weather = self.process_forecasted_data()
        print(meteo_and_prod.columns)

        return meteo_and_prod, self.forecasted_weather