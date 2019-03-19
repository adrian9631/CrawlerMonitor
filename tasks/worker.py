import os
from celery import Celery, platforms
from kombu import Exchange, Queue

platforms.C_FORCE_ROOT = True

broker = 'amqp://user:password@127.0.0.1:5672//'
backend = 'mongodb://user:password@127.0.0.1:27017/admin'
# backend = 'redis://:password@127.0.0.1:6379/2'

tasks = ['tasks.spider',]

app = Celery('tasks', broker=broker, backend=backend, include=tasks)

app.conf.update(

    CELERY_TIMEZONE='Asia/Shanghai',
    CELERY_ENABLE_UTC=True,
    CELERY_ACCEPT_CONTENT=['json', 'pickle'],
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
    CELERYD_MAX_TASKS_PER_CHILD=500,
    CELERY_BROKER_HEARTBEAT=0,

    CELERY_QUEUES=(
        Queue('crawl_queue', exchange=Exchange('crawl_queue', type='direct'), routing_key='crawl'),
        Queue('parse_queue', exchange=Exchange('parse_queue', type='direct'), routing_key='parse'),
    ),

)
