from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor 
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import TimeSeriesSplit
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
import pickle 

class ModelTeacher:
    def __init__(self, data, TARGET_VARIABLES, N_ESTIMATORS, MAX_DEPTH, SEED, RANDOM_STATE):
        self.data = data
        self.TARGET_VARIABLES = TARGET_VARIABLES
        self.N_ESTIMATORS = N_ESTIMATORS
        self.RANDOM_STATE = RANDOM_STATE
        self.MAX_DEPTH = MAX_DEPTH
        self.SEED=SEED
    
    def wape(self, y_pred, y_true):
        return np.sum(np.abs(y_true - y_pred)) / np.sum(np.abs(y_true))

    def plot_predictions_vs_true(
        self,
        y_pred, 
        y
    ):
    
        fig, ax = plt.subplots(figsize=(8, 6))

        sns.scatterplot(x=y_pred, y=y, alpha=0.3, ax=ax)
        ax.set_title(f"MAE: {mean_absolute_error(y_pred, y):.2f}, R2: {r2_score(y_pred, y):.2f}, WAPE: {self.wape(y_pred, y):.2f}")
        ax.set_xlabel("Предсказание")
        ax.set_ylabel("Выработка")
        ax.plot([0, len(y)], [0, len(y_pred)], c='r', linestyle='--')

        fig.savefig("src/content/model_metrics.png")

        plt.close(fig) 
        return fig

    def train_model(self):
        y = self.data['production']
        x = self.data.drop(columns=['production', 'date'])
        x_train, x_test, y_train, y_test = train_test_split(x,
                                                    y, 
                                                    test_size=0.2)

        param_grid = { 
        'max_depth': [5, 10, 15, None], 
        'min_samples_split': [2, 5, 10], 
        'min_samples_leaf': [1, 2, 4],
        'max_features': [1.0, 'sqrt', 'log2'],
        'ccp_alpha': [0.0, 0.001, 0.01],
        'criterion': ['squared_error', 'absolute_error', 'friedman_mse']
        }
        
        tscv = TimeSeriesSplit(n_splits=10)
        
        model = GridSearchCV(
            RandomForestRegressor(random_state=self.RANDOM_STATE),
            param_grid,
            cv=tscv,
            scoring='neg_root_mean_squared_error',
            n_jobs=-1
        )
        
        model.fit(x_train, y_train)
        with open('my_model.pkl', 'wb') as f:
            pickle.dump(model, f)
        return (model, model.predict(x_test), y_test)

    
    def get_predict(self, predict_df: pd.DataFrame):
        
        X_new = predict_df[self.feature_names]

        predictions = self.model.predict(X_new)

        result_df = predict_df.copy()
        result_df['production'] = predictions
        
        return result_df
