from flask import Flask, render_template
import pika
import threading
import time
import random
import json
import os

app = Flask(__name__)

amqp_url = '<url_from_cloudamqps>'
params = pika.URLParameters(amqp_url)

def get_sensor_data():
    data = {
        'temperature': round(random.uniform(15.0, 30.0), 2),
        'humidity': round(random.uniform(30.0, 80.0), 2),
        'motion': random.choice([True, False]),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    return data

def send_sensor_data():
    while True:
        sensor_data = get_sensor_data()
        message = json.dumps(sensor_data)
        try:
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            exchange_name = 'sensor_data_exchange'
            channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
            channel.basic_publish(exchange=exchange_name, routing_key='', body=message)
            print(f" Sent {message}")
            connection.close()
        except Exception as e:
            print(f"Error sending message: {e}")
        time.sleep(5) 

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    threading.Thread(target=send_sensor_data).start()
    app.run(debug=True, port=5001)
