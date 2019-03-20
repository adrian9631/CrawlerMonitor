import sys
import time
import threading
import logging

from worker import app
from statsd import StatsClient
from celery.events import EventReceiver
from kombu import Connection as BrokerConnection

# logging message
logging.basicConfig(level = logging.INFO,format ='[%(asctime)s : %(levelname)s/%(processName)s] %(message)s')
logger = logging.getLogger(__name__)

class CeleryMonitor(object):
    def __init__(self, broker, interval=1):
        self.interval = interval
        self.state = app.events.State()
        self.statsd_conn = StatsClient(host='localhost', port=8125)
        self.broker_conn = BrokerConnection(broker)
        self.timers_list = []

    # monitor the task and status of worker with functions
    def run_loop(self):
        while True:
            try:
                with self.broker_conn as conn:
                    recv = EventReceiver(conn, handlers={
                        'task-sent': self.on_task_sent,
                        'task-failed': self.on_task_failed,
                        'task-retried': self.on_task_retried,
                        'task-started': self.on_task_started,
                        'task-succeeded': self.on_task_succeeded,
                        'task-received': self.on_task_received,
                        'task-rejected': self.on_task_rejected,
                        'task-revoked': self.on_task_revoked,
                        'worker-online': self.on_worker_online,
                        'worker-heartbeat': self.on_worker_heartbeat,
                        'worker-offline': self.on_worker_offline,
                    })
                    recv.capture(limit=None, timeout=None, wakeup=True)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception:
                raise
            time.sleep(self.interval)

    # all about the tasks

    def on_task_sent(self, event): # TODO
        self.state.event(event)
        task = self.state.tasks.get(event['uuid'])
        self.statsd_conn.incr('tasks.sent')

    def on_task_received(self, event): # TODO
        self.state.event(event)
        task = self.state.tasks.get(event['uuid'])
        self.statsd_conn.incr('tasks.received')

    def on_task_started(self, event):
        self.state.event(event)
        task = self.state.tasks.get(event['uuid'])
        logger.info('Task {}[{}] started'.format(task.name, task.uuid))
        self.statsd_conn.incr('tasks.started')
        mark = 'task.{}.recorder'.format(task.uuid)
        self.timer_start(mark)

    def on_task_succeeded(self, event):
        self.state.event(event)
        task = self.state.tasks.get(event['uuid'])
        logger.info('Task {}[{}] succeeded'.format(task.name, task.uuid))
        self.statsd_conn.incr('tasks.succeeded')
        mark = 'task.{}.recorder'.format(task.uuid)
        self.timer_stop(mark)

    def on_task_failed(self, event): # TODO
        self.state.event(event)
        task = self.state.tasks.get(event['uuid'])
        logger.warning('Task {}[{}] failed'.format(task.name, task.uuid))
        self.statsd_conn.incr('tasks.failed')

    def on_task_retried(self, event): # TODO
        self.state.event(event)
        task = self.state.tasks.get(event['uuid'])
        logger.warning('Task {}[{}] retried'.format(task.name, task.uuid))
        self.statsd_conn.incr('tasks.retried')

    def on_task_rejected(self, event): # TODO
        self.state.event(event)
        task = self.state.tasks.get(event['uuid'])

    def on_task_revoked(self, event): # TODO
        self.state.event(event)
        task = self.state.tasks.get(event['uuid'])

    # all about the status of the workers

    def on_worker_online(self, event): # TODO
        self.state.event(event)
        worker = self.state.workers.get(event['hostname'])
        mark = 'worker.{}.recorder'.format(worker.hostname)
        self.timer_start(mark)

    def on_worker_heartbeat(self, event):
        self.state.event(event)
        worker = self.state.workers.get(event['hostname'])
        key_pro = 'worker.{}.processed'.format(worker.hostname)
        key_act = 'worker.{}.active'.format(worker.hostname)
        if worker.processed is None: worker.processed = 0
        if worker.active is None: worker.active = 0
        self.statsd_conn.gauge(key_pro, worker.processed)
        self.statsd_conn.gauge(key_act, worker.active)

    def on_worker_offline(self, event): # TODO
        self.state.event(event)
        worker = self.state.workers.get(event['hostname'])
        mark = 'worker.{}.recorder'.format(worker.hostname)
        self.timer_stop(mark)

    # statsd timer record start
    def timer_start(self, mark):
        timer = self.statsd_conn.timer(mark)
        timer.start()
        self.timers_list.append(timer)

    # statsd timer record stop
    def timer_stop(self, mark):
        for timer in self.timers_list:
            if timer.stat == mark:
                timer.stop()
                self.timers_list.remove(timer)
