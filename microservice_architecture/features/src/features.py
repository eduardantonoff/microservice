import pika
import numpy as np
import json
import time
import uuid
from sklearn.datasets import load_diabetes

# Загрузка датасета
X, y = load_diabetes(return_X_y=True)

# Установление соединения с RabbitMQ
def create_connection():
    return pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))

try:
    connection = create_connection()
    channel = connection.channel()

    # Объявление очередей
    channel.queue_declare(queue='y_true')
    channel.queue_declare(queue='features')

    print("Подключено к RabbitMQ и очереди объявлены.")

    while True:
        try:
            # Выбор случайной строки
            random_row = np.random.randint(0, X.shape[0])

            # Генерация уникального ID / вместо datetime
            message_id = str(uuid.uuid4())

            # Подготовка сообщений
            message_y_true = {
                'id': message_id,
                'body': y[random_row]
            }
            message_features = {
                'id': message_id,
                'body': X[random_row].tolist()
            }

            # Публикация сообщений
            channel.basic_publish(
                exchange='',
                routing_key='y_true',
                body=json.dumps(message_y_true)
            )
            print(f'Опубликовано y_true с ID: {message_id}')

            channel.basic_publish(
                exchange='',
                routing_key='features',
                body=json.dumps(message_features)
            )
            print(f'Опубликованы features с ID: {message_id}')

            # Ожидание перед следующей итерацие
            time.sleep(10)

        except pika.exceptions.AMQPConnectionError as e:
            print(f'Ошибка соединения: {e}. Повторное подключение...')
            connection = create_connection()
            channel = connection.channel()
            channel.queue_declare(queue='y_true')
            channel.queue_declare(queue='features')
            time.sleep(5)

        except Exception as e:
            print(f'Неожиданная ошибка: {e}')
            time.sleep(10)

except pika.exceptions.AMQPConnectionError as e:
    print(f'Не удалось подключиться к RabbitMQ: {e}')