# ☀️ Solar Power Generation Predictor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red.svg)](https://github.com/Wkor)

![Solar Power Generation Predictor Banner](https://amplussolar.com/blog/wp-content/uploads/2024/05/blog-topheader.webp)

> A powerful desktop application that predicts solar power plant generation using machine learning and historical weather data.

## 📋 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [How It Works](#-how-it-works)
- [Installation](#-installation)
- [Usage](#-usage)
- [Input Format](#-input-format)
- [Technical Details](#-technical-details)
- [Output](#-output)
- [Requirements](#-requirements)
- [License](#-license)
- [Contributing](#-contributing)

## 🎯 Overview

The Solar Power Generation Predictor is a desktop application designed to help solar power plant operators forecast energy production. By combining historical generation data with weather information, the app uses machine learning to provide accurate predictions for the next 1-3 days.

## ✨ Features

- **📍 Location-Based Forecasting**: Input any coordinates to get localized weather data
- **📊 Smart Data Processing**: Automatic cleaning of historical data (removes NaNs, duplicates, and anomalies)
- **🤖 Machine Learning**: Utilizes Random Forest algorithm with hyperparameter tuning via GridSearchCV
- **📈 Model Evaluation**: Visualizes model performance on test data (20% of historical data)
- **📱 User-Friendly Interface**: Simple GUI for easy interaction
- **📤 Exportable Results**: View forecasts in a clean table format

## 🔧 How It Works

1. **Input Parameters**: User provides:
   - Geographic coordinates (longitude, latitude)
   - Forecast horizon (1-3 days)
   - Historical generation data (Excel file)

2. **Data Collection**:
   - Fetches historical weather data from Open-Meteo API
   - Matches weather data with generation periods

3. **Data Processing**:
   - Merges weather and generation datasets
   - Splits data (80% training, 20% testing)
   - Removes anomalies and missing values

4. **Model Training**:
   - Performs hyperparameter tuning using GridSearchCV
   - Trains Random Forest model on optimal parameters

5. **Results**:
   - Shows model performance metrics
   - Generates forecasts for specified period
   - Presents results in an easy-to-read table

## 💻 Installation

Run from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/Solar-Power-Generation-Predictor.git
cd Solar-Power-Generation-Predictor

# Install required packages
pip install -r requirements.txt

# Run the application
python app.py
