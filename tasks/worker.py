import os
from celery import Celery, platforms
from kombu import Exchange, Queue
from utils import get_config_values

platforms.C_FORCE_ROOT = True

broker = get_config_values('celery','broker')
backend = get_config_values('celery','backend')
tasks = get_config_values('celery','tasks')

app = Celery('tasks', broker=broker, backend=backend, include=tasks)

app.conf.update(

    CELERY_TIMEZONE='Asia/Shanghai',
    CELERY_ENABLE_UTC=True,
    CELERY_ACCEPT_CONTENT=['json', 'pickle'],
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
    CELERYD_MAX_TASKS_PER_CHILD=500,
    CELERY_BROKER_HEARTBEAT=0,
    CELERYD_SEND_EVENTS=True,
    CELERYD_PREFETCH_MULTIPLIER=2,
    CELERY_QUEUES=(
        Queue('crawl_queue', exchange=Exchange('crawl_queue', type='direct'), routing_key='crawl'),
        Queue('parse_queue', exchange=Exchange('parse_queue', type='direct'), routing_key='parse'),
    ),

)
