from celery import Celery

app = Celery('tasks', broker="amqp://rabbit:5672", backend='redis://redis')
@app.task
def add(x, y):
    return x + y
