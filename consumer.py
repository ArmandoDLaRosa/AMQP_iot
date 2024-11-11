from flask import Flask, render_template
from flask_socketio import SocketIO
import pika
import json
import os
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')

amqp_url = '<url_from_cloudamqps>'
params = pika.URLParameters(amqp_url)

@app.route('/')
def index():
    return render_template('consumer.html')

def consume():
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    exchange_name = 'sensor_data_exchange'
    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange_name, queue=queue_name)

    def callback(ch, method, properties, body):
        message = body.decode()
        print(f" [x] Received {message}")
        sensor_data = json.loads(message)
        socketio.emit('new_sensor_data', sensor_data)

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

def start_consumer():
    eventlet.spawn(consume)

if __name__ == '__main__':
    start_consumer()
    socketio.run(app, debug=True, port=5000)
