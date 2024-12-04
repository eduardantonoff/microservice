import pika
import pickle
import numpy as np
import json
import sys
import signal

# Загрузка сериализованной модели
with open('/usr/src/app/myfile.pkl', 'rb') as pkl_file:
    regressor = pickle.load(pkl_file)

# Функция для корректного завершения работы
def shutdown(signum, frame):
    print("Завершение работы...")
    connection.close()
    sys.exit(0)

# Регистрация обработчиков
signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

def create_connection():
    return pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))

try:
    connection = create_connection()
    channel = connection.channel()

    # Объявление очередей
    channel.queue_declare(queue='features')
    channel.queue_declare(queue='y_pred')

    print("Подключено к RabbitMQ.")

    def callback(ch, method, properties, body):
        try:
            message = json.loads(body)
            message_id = message['id']
            features = np.array(message['body']).reshape(1, -1)
            print(f'Получены признаки для ID={message_id}: {features}')

            # Предсказание 
            pred = regressor.predict(features)[0]

            # Подготовка сообщения с резкльтатом 
            message_pred = {
                'id': message_id,
                'body': pred
            }

            # Публикация 
            channel.basic_publish(
                exchange='',
                routing_key='y_pred',
                body=json.dumps(message_pred)
            )
            print(f'Опубликован y_pred для ID={message_id}: {pred}')

        except Exception as e:
            print(f'Ошибка при обработке сообщения: {e}')

    # Начало обработки сообщений
    channel.basic_consume(queue='features', on_message_callback=callback, auto_ack=True)
    print('Ожидание сообщений.')
    channel.start_consuming()

except pika.exceptions.AMQPConnectionError as e:
    print(f'Не удалось подключиться к RabbitMQ: {e}')