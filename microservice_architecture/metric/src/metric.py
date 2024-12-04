import pika
import json
import pandas as pd
import time
import os
import sys
import signal

LOG_FILE = './logs/metric_log.csv'
COLUMNS = ['id', 'y_true', 'y_pred', 'absolute_error']

# Проверить, что директория существует
os.makedirs('./logs', exist_ok=True)

# Инициализация CSV файла, если он не существует
if not os.path.isfile(LOG_FILE):
    pd.DataFrame(columns=COLUMNS).to_csv(LOG_FILE, index=False)

# Функция для корректного завершения работы
def shutdown(signum, frame):
    print("Завершение работы...")
    connection.close()
    sys.exit(0)

# Регистрация обработчиков сигналов для корректного завершения работы
signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

def create_connection():
    return pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))

try:
    connection = create_connection()
    channel = connection.channel()

    # Объявление очередей
    channel.queue_declare(queue='y_true')
    channel.queue_declare(queue='y_pred')

    print("Подключено к RabbitMQ.")

    # Словари для хранения сообщений по ID
    y_true_dict = {}
    y_pred_dict = {}

    def callback(ch, method, properties, body):
        try:
            message = json.loads(body)
            message_id = message['id']

            if method.routing_key == 'y_true':
                y_true_dict[message_id] = message['body']
                print(f"Получено y_true для ID: {message_id}")
            elif method.routing_key == 'y_pred':
                y_pred_dict[message_id] = message['body']
                print(f"Получено y_pred для ID: {message_id}")

            # Проверка наличия y_true и y_pred
            if message_id in y_true_dict and message_id in y_pred_dict:
                y_true = y_true_dict.pop(message_id)
                y_pred = y_pred_dict.pop(message_id)
                absolute_error = abs(y_true - y_pred)

                # Добавление в CSV
                with open(LOG_FILE, 'a') as f:
                    f.write(f"{message_id},{y_true},{y_pred},{absolute_error}\n")

                print(f"Записаны данные для ID: {message_id} | y_true: {y_true}, y_pred: {y_pred}, absolute_error: {absolute_error}")

        except Exception as e:
            print(f'Ошибка при обработке сообщения: {e}')

    # Начало обработки сообщений из обеих очередей
    channel.basic_consume(queue='y_true', on_message_callback=callback, auto_ack=True)
    channel.basic_consume(queue='y_pred', on_message_callback=callback, auto_ack=True)

    print('Ожидание сообщений.')
    channel.start_consuming()

except pika.exceptions.AMQPConnectionError as e:
    print(f'Не удалось подключиться к RabbitMQ: {e}')