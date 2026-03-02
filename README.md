# Solar-Power-Generation-Predictor


![Иллюстрация к проекту](https://amplussolar.com/blog/wp-content/uploads/2024/05/blog-topheader.webp)

It is a desktop app for predict solar power plants generation.

**How it works?**
- user enter longitude, latitude of solar power-plant, days for forecasting (1 - 3)
- user enter historical generation xlsx-tablet in next format: date(yyyy-mm-dd), id (of solar modules array), production (in kW*h)
- program gets historical meteo-data of historical production period on Open-Meteo API-services
- program process all data (delete NaNs, dublicates and anomalies)
- program starts learn AI-model (Gradient Boosting Regressor) using historical meteo-data and historical production-data
- program view results of work model on test-data (20% of historical data)
- program gives results of forecasting (in tablet view)

**How to use it?**
- run app.py or download installer, install .exe-file (in develop) and run it 
- enter longitude, latitude of solar power-plant, days for forecasting (1 - 3)
- enter historical generation xlsx-tablet in next format: date(yyyy-mm-dd), id (of solar modules array), production (in kW*h) of your plant or test data (production.xlsx)
- wait result :)
