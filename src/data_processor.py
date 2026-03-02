import pandas as pd
import numpy as np 

class DataProcessor:
    def __init__(self, production, historical_weather, forecasted_weather, SIGNS, DAYS, ID_STATION):
        self.production = production
        self.historical_weather = historical_weather
        self.SIGNS = SIGNS
        self.forecasted_weather = forecasted_weather
        self.DAYS = DAYS
        self.ID_STATION = ID_STATION
        
    def to_num(self):
        self.production["production"] = pd.to_numeric(self.production["production"], errors="coerce")
    
    def delete_NaNs(self):
        self.production = self.production.dropna(subset=['production'])
        
    def sort_per_date(self):
        self.meteo_and_prod.sort_values(by='valid_time', inplace=True)
        
    def dele_dublicates(self):
        self.production = self.production.drop_duplicates(subset=['date', 'id_station'], keep='first')
        self.production.loc[:, 'date'] = pd.to_datetime(self.production['date']).dt.date
        
    def to_datetime_format(self):
        self.historical_weather["date"] = pd.to_datetime(self.historical_weather['date']).dt.date
        self.production["date"] = pd.to_datetime(self.production["date"]).dt.date
    
    def merge_data(self):
        self.meteo_and_prod = pd.merge(
            self.historical_weather,
            self.production,
            on='date',
            how='left',
        )

        sum_columns = ['diffuse_radiation', 'terrestrial_radiation']
        mean_columns = ['cloud_cover', 'relative_humidity_2m', 'temperature_2m']
        
        for col in self.meteo_and_prod.columns:
            if col not in ['id_station', 'date', 'production']:
                if col in mean_columns and pd.api.types.is_numeric_dtype(self.meteo_and_prod[col]):
                    mean_columns.append(col) if col not in mean_columns else None
                elif pd.api.types.is_numeric_dtype(self.meteo_and_prod[col]):
                    sum_columns.append(col)
    
        agg_dict = {}
        for col in sum_columns:
            agg_dict[col] = 'sum'
        for col in mean_columns:
            if col in self.meteo_and_prod.columns and pd.api.types.is_numeric_dtype(self.meteo_and_prod[col]):
                agg_dict[col] = 'mean'
    
        if 'production' in self.meteo_and_prod.columns:
            agg_dict['production'] = 'first'
    
        self.meteo_and_prod = (
            self.meteo_and_prod.groupby(['id_station', 'date'])
            .agg(agg_dict)
            .reset_index()
        )

        self.meteo_and_prod = self.meteo_and_prod.rename(columns={'date': 'valid_time'})

        self.meteo_and_prod['production'] = self.meteo_and_prod['production'].round(2)

            
    def delete_anomalies(self):
        q1 = self.meteo_and_prod['production'].quantile(0.25)
        q3 = self.meteo_and_prod['production'].quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr 
        upper_bound = q3 + 1.5 * iqr

        self.meteo_and_prod.loc[(self.meteo_and_prod['production'] < lower_bound) | (self.meteo_and_prod['production'] > upper_bound), 'production'] = np.nan
        
            
    def process_forecast_data(self):
        self.forecasted_weather['date'] = pd.to_datetime(self.forecasted_weather['date']).dt.date

        sum_columns = ['diffuse_radiation', 'terrestrial_radiation']
        mean_columns = ['cloud_cover', 'relative_humidity_2m', 'temperature_2m']

        for col in self.forecasted_weather.columns:
            if col not in ['id_station', 'date', 'production'] and pd.api.types.is_numeric_dtype(self.forecasted_weather[col]):
                if col not in mean_columns:
                    sum_columns.append(col)

        agg_dict = {}

        for col in sum_columns:
            agg_dict[col] = 'sum'

        for col in mean_columns:
            if col in self.forecasted_weather.columns:
                agg_dict[col] = 'mean'

        if 'production' in self.forecasted_weather.columns:
            agg_dict['production'] = 'sum' 

        group_cols = ['date']
        if 'id_station' in self.forecasted_weather.columns:
            group_cols.append('id_station')

        self.forecasted_weather = (
            self.forecasted_weather.groupby(group_cols)
            .agg(agg_dict)
            .reset_index()
        )
        
        self.forecasted_weather["id_station"] = [(int)(self.ID_STATION)] * len(self.forecasted_weather["cloud_cover"]) 
    
    def remove_indexes(self, df=None, column_name='index'):
        if df is not None:
            cols_to_remove = []
            
            if isinstance(column_name, str):
                if column_name in df.columns:
                    cols_to_remove.append(column_name)
            elif isinstance(column_name, list):
                for col in column_name:
                    if col in df.columns:
                        cols_to_remove.append(col)

            for col in df.columns:
                if str(col).startswith('Unnamed:') or str(col).strip() == '':
                    cols_to_remove.append(col)
            
            cols_to_remove = list(set(cols_to_remove))
            
            if cols_to_remove:
                return df.drop(columns=cols_to_remove)
            return df
        else:
            if hasattr(self, 'meteo_and_prod') and self.meteo_and_prod is not None:
                self.meteo_and_prod = self.remove_indexes(self.meteo_and_prod, column_name)
            
            if hasattr(self, 'forecasted_weather') and self.forecasted_weather is not None:
                self.forecasted_weather = self.remove_indexes(self.forecasted_weather, column_name)
    
    def remove_all_indexes(self):
        index_names = ['index', 'level_0', 'Unnamed: 0', 'Unnamed: 0.1', '']
        
        if hasattr(self, 'meteo_and_prod') and self.meteo_and_prod is not None:
            for idx_name in index_names:
                if idx_name in self.meteo_and_prod.columns:
                    self.meteo_and_prod = self.meteo_and_prod.drop(columns=[idx_name])
            
            cols_to_remove = [col for col in self.meteo_and_prod.columns 
                            if str(col).startswith('Unnamed:') or str(col).strip() == '']
            if cols_to_remove:
                self.meteo_and_prod = self.meteo_and_prod.drop(columns=cols_to_remove)
        
        if hasattr(self, 'forecasted_weather') and self.forecasted_weather is not None:
            for idx_name in index_names:
                if idx_name in self.forecasted_weather.columns:
                    self.forecasted_weather = self.forecasted_weather.drop(columns=[idx_name])

            cols_to_remove = [col for col in self.forecasted_weather.columns 
                            if str(col).startswith('Unnamed:') or str(col).strip() == '']
            if cols_to_remove:
                self.forecasted_weather = self.forecasted_weather.drop(columns=cols_to_remove)
    
    def reset_and_remove_indexes(self):
        if hasattr(self, 'meteo_and_prod') and self.meteo_and_prod is not None:
            self.meteo_and_prod = self.meteo_and_prod.reset_index(drop=True)
        
        if hasattr(self, 'forecasted_weather') and self.forecasted_weather is not None:
            self.forecasted_weather = self.forecasted_weather.reset_index(drop=True)

    def process_data(self):
        self.to_num()
        self.delete_NaNs()
        self.dele_dublicates()
        self.to_datetime_format()
        self.merge_data()
        self.sort_per_date()
        self.delete_anomalies()
        self.process_forecast_data()
        self.remove_all_indexes() 
        return self.meteo_and_prod, self.forecasted_weather