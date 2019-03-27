import time
import requests
from tasks.worker import app
from monitor import PrometheusMonitor
from celery.utils.log import get_task_logger
from multiprocessing import Process
from utils import get_config_values

logger = get_task_logger(__name__)

def monitor():
    # turn on the monitor
    broker = get_config_values('celery','broker')
    daemon = PrometheusMonitor(app=app, broker=broker)
    daemon.run_loop()

def tasks():

    # stock symbol
    symbols = get_config_values('spider','symbols')
    # article category
    categorys = get_config_values('spider','categorys')

    # get cookies
    result = app.send_task('tasks.spider.get_cookies', queue='crawl_queue')
    while not result.ready():
        time.sleep(1)
    cookies = result.get()

    # send tasks
    for symbol in symbols:
        app.send_task('tasks.spider.comment', [cookies, symbol], queue='crawl_queue')
    for category in categorys:
        app.send_task('tasks.spider.article', [cookies, category], queue='crawl_queue')

def test():

    p = Process(target=monitor, args=())
    p.start()

    time.sleep(10)
    tasks()

    p.join()

if __name__ == "__main__":
    test()
