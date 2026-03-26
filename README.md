# Solar-Power-Generation-Predictor


![Иллюстрация к проекту](https://amplussolar.com/blog/wp-content/uploads/2024/05/blog-topheader.webp)

It is a desktop app for predict solar power plants generation.

**How it works?**
- The user enters the longitude and latitude of the solar power plant, as well as the number of days for forecasting (1–3).
- The user uploads a historical generation file in Excel format (.xlsx) with the following columns: date (yyyy-mm-dd), id (solar module array identifier), and production (in kWh).
- The program retrieves historical weather data for the corresponding period from the Open-Meteo API.
- The program processes the data by removing NaNs (in historial generation file), duplicates, and anomalies.
- The program runs a hyperparameter tuning process to select the best model (model - Random Forest, hyperparameter search algorithm - GridSearchCV)
- The program shows results of model performance on test data (20% of historical data)
- Program provides forecasting results (in tablet view)

**How to use it?**
- Run app.py or download installer, install .exe-file (in develop) and run it.
- Enter longitude, latitude of solar power-plant, days for forecasting (1 - 3).
- Enter historical generation xlsx-table in next format: date(yyyy-mm-dd), id (of solar modules array), production (in kW*h) of your plant or test data (production.xlsx).
- Wait result :).























