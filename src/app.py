import customtkinter as ctki
from data_processor import DataProcessor
from forecasted_data_loader import ForecastedDataLoader
from historical_data_loader import HistoricalDataLoader
from model_teacher import ModelTeacher
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

SLIDER_MIN = 1
SLIDER_MAX = 3
SLIDER_DEFAULT = 2  
PARAMETERS = [                    
    "diffuse_radiation",                 
    "terrestrial_radiation",         
    "cloud_cover",                   
    "relative_humidity_2m",
    "temperature_2m",     
    "surface_pressure",
    "wind_speed_10m"           
]

class SolarApp(ctki.CTk):
    def __init__(self):
        super().__init__()

        self.production_fp = None
        self.result_fd = None
        self.metrics_image = None
        self.id_station = None
        
        self.title("Solar PPG Forecaster")
        self.minsize(width=1300, height=800)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.iconbitmap("src/content/icon.ico")

        self._create_input_panel()

    def _create_input_panel(self):
        self.input_frame = ctki.CTkFrame(self, fg_color="#242424", border_color="#006C8D", border_width=3)
        self.output_frame = ctki.CTkFrame(self, fg_color="#242424", border_color="#006C8D", border_width=3)
        
        self.input_frame.pack(side="top", fill="x", padx=10, pady=10)
        self.output_frame.pack(side="bottom", fill="x", padx=10, pady=50)

        self.input_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1, uniform="equal")

        self.lat_entry = ctki.CTkEntry(self.input_frame, placeholder_text="Широта", 
                                    height=40, width=30, font=("Arial", 12))
        self.lat_entry.grid(row=0, column=0, padx=(10, 5), pady=15, sticky="ew")
        
        self.lon_entry = ctki.CTkEntry(self.input_frame, placeholder_text="Долгота", 
                                    height=40, width=30, font=("Arial", 12))
        self.lon_entry.grid(row=0, column=1, padx=5, pady=15, sticky="ew")
        
        self.st_number_entry = ctki.CTkEntry(self.input_frame, placeholder_text="Номер группы ф. элементов", 
                                            height=40, width=30, font=("Arial", 12))
        self.st_number_entry.grid(row=0, column=2, padx=5, pady=15, sticky="ew")
        
        slider_container = ctki.CTkFrame(self.input_frame, fg_color="transparent")
        slider_container.grid(row=0, column=3, padx=10, pady=10, sticky="ew", columnspan=2)
        slider_container.grid_columnconfigure(0, weight=1)
        
        self.current_val_label = ctki.CTkLabel(slider_container, text=f"Дни: {SLIDER_DEFAULT}", 
                                            font=("Arial", 12, "bold"))
        self.current_val_label.pack(pady=(0, 5))
        
        self.slider = ctki.CTkSlider(slider_container, from_=SLIDER_MIN, to=SLIDER_MAX, 
                                    number_of_steps=SLIDER_MAX - SLIDER_MIN,
                                    command=self._slider_callback, height=20)
        self.slider.set(SLIDER_DEFAULT)
        self.slider.pack(fill="x", padx=10, pady=5)

        self.load_btn = ctki.CTkButton(self.input_frame, border_color="#C4C4C4", border_width=2, 
                                    text="Загрузить данные по выработке", height=40, font=("Georgia", 13, "bold"),
                                    command=self._load_data_handler, width=10)
        self.load_btn.grid(row=0, column=5, padx=5, pady=15, sticky="ew")
        
        self.start_btn = ctki.CTkButton(self.input_frame, border_color="#C4C4C4", border_width=2, 
                                        text="Начать обучение", height=40, font=("Georgia", 13, "bold"),
                                        fg_color="#28a745", hover_color="#218838",
                                        command=self.start_program, width=10)
        self.start_btn.grid(row=0, column=6, padx=(5, 10), pady=15, sticky="ew")
        
    def _download_results(self, result_file, predicts):
        self.result_fd = ctki.filedialog.askdirectory(title="Укажите путь к целевой папке")
        result_file["production"] = predicts
        result_file['date'] = pd.to_datetime(result_file['date'])

        result_file['date'] = result_file['date'].dt.tz_localize(None)
        result_file.to_excel(f"{self.result_fd}/result.xlsx")
        
    def _slider_callback(self, value):
        self.current_val_label.configure(text=f"Дни: {int(value)}")

    def _load_data_handler(self):
        self.production_fp = ctki.filedialog.askopenfilename(title="Выберите файл")

    def start_program(self):
        lat = self.lat_entry.get()
        lon = self.lon_entry.get()

        production = pd.read_excel(self.production_fp)
        start_date = production["date"][0]
        end_date = production["date"][len(production["date"]) - 1]

        self.id_station = self.st_number_entry.get()
        
        hist_dl = HistoricalDataLoader(lat, lon, start_date, end_date, PARAMETERS)
        hist_data = hist_dl.load_data()
    
        forec_dl = ForecastedDataLoader(PARAMETERS, str(end_date)[0:10], str(end_date + dt.timedelta(days=self.slider.get() - 1))[0:10], self.lat_entry.get(), lon)
        forec_data = forec_dl.load_data()
        
        processor = DataProcessor(production, hist_data, forec_data, PARAMETERS, self.slider.get(), self.id_station)
        meteo_and_prod, forec_data = processor.process_data()
        print(meteo_and_prod.head())
        model_teacher = ModelTeacher(meteo_and_prod, ["production"], 50, 20, 24, 42)
        model_and_predicts = model_teacher.train_model()
        model = model_and_predicts[0]
        
        y = meteo_and_prod["production"]
        x = meteo_and_prod.drop(columns=['date', 'production'], axis=1)
        x_train, x_test, y_train, y_test = train_test_split(x,
                                                    y, 
                                                    test_size=0.2, random_state=42)
        
        predicts = model.predict(x_test[model.feature_names_in_])
        
        fact = y_test
        predicts = model_and_predicts[1]
        fact = model_and_predicts[2]
        model_teacher.plot_predictions_vs_true(predicts, fact)
        metrics_image = ctki.CTkImage(light_image=Image.open("src/content/model_metrics.png"), size=(800, 600))
        metrics_image_label = ctki.CTkLabel(self.output_frame, image=metrics_image, text="")
        metrics_image_label.pack(pady=10)
        predicts = model.predict(forec_data[model.feature_names_in_])
        model_teacher.plot_predictions_vs_true(predicts, predicts)
        result_file = forec_data.copy() 
        download_button = ctki.CTkButton(self.output_frame, border_color="#C4C4C4", border_width=2, 
                                        text="Получить результат прогнозирования", height=40, font=("Georgia", 13, "bold"),
                                        fg_color="#28a745", hover_color="#218838",
                                        command=lambda:self._download_results(result_file, predicts), width=10)
        
        print(forec_data.head())
        download_button.pack(pady=10)


if __name__ == "__main__":
    app = SolarApp()
    app.mainloop()
    

