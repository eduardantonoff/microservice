import os
import sys
import time
import signal
import pandas as pd
import matplotlib.pyplot as plt

LOG_FILE = './logs/metric_log.csv'
PLOT_FILE = './logs/error_distribution.png'

# Функция для корректного завершения работы
def shutdown(signum, frame):
    print("Завершение работы...")
    sys.exit(0)

# Регистрация обработчиков 
signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

# Проверка, что директория logs существует
os.makedirs('./logs', exist_ok=True)

last_line = 0

while True:
    try:
        if os.path.isfile(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
                if len(lines) > 1 and len(lines) > last_line:
                    # Чтение новых строк
                    new_data = pd.read_csv(LOG_FILE, skiprows=range(1, last_line + 1))
                    last_line = len(lines) - 1

                    # Чтение CSV 
                    metric_log = pd.read_csv(LOG_FILE)

                    # Построение гистограммы
                    plt.figure(figsize=(16, 9))
                    plt.hist(metric_log['absolute_error'], bins=20, color='grey', edgecolor='black')
                    plt.title('Distribution of Absolute Errors')
                    plt.xlabel('Absolute Error')
                    plt.ylabel('Frequency')
                    plt.tight_layout()

                    # Сохранение 
                    plt.savefig(PLOT_FILE)
                    plt.close()
                    print("Гистограмма обновлена.")

        else:
            print(f"{LOG_FILE} не найден. Ожидание создания файла.")

        # Ожидание перед следующей итерацией
        time.sleep(10)

    except Exception as e:
        print(f'Ошибка при построении графика: {e}')
        time.sleep(10)