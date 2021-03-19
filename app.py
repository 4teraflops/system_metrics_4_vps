import psutil
import time
import json
from config import admin_id, webhook_url
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server
import requests
from loguru import logger

logger.add(f'log/{__name__}.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')


def do_alarm(t_alarmtext):
    headers = {"Content-type": "application/json"}
    payload = {"text": f"{t_alarmtext}", "chat_id": f"{admin_id}"}
    requests.post(url=webhook_url, data=json.dumps(payload), headers=headers)


def get_cpu_procent():
    #print(f'psutil.cpu_percent(): {psutil.cpu_percent()}')
    return psutil.cpu_percent()


def get_virtual_memory_procent_usage():
    #print(f'psutil.virtual_memory().percent: {psutil.virtual_memory().percent}')
    return psutil.virtual_memory().percent


def get_disc_usage():
    #print(f'psutil.disk_usage.used.precent:{psutil.disk_usage("/").percent}')
    return psutil.disk_usage("/").percent


class CustomCollector(object):
    def __init__(self):
        pass

    def collect(self):
        cpu_usage = GaugeMetricFamily('cpu_procent_usage', '%')
        cpu_usage_metric = get_cpu_procent()
        cpu_usage.add_metric([], cpu_usage_metric)

        ram_usage = GaugeMetricFamily('ram_precent_usage', '%')
        ram_usage_metric = get_virtual_memory_procent_usage()
        ram_usage.add_metric([], ram_usage_metric)

        disk_usage = GaugeMetricFamily('disk_usage', '%')
        disk_usage_metric = get_disc_usage()
        disk_usage.add_metric([], disk_usage_metric)

        yield cpu_usage
        yield ram_usage
        yield disk_usage


if __name__ == '__main__':
    try:
        start_http_server(8000)
        REGISTRY.register(CustomCollector())
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Program stopped')
    except Exception as e:
        t_alarmtext = f'prometheus-custom-collector (app.py):\n {str(e)}'
        do_alarm(t_alarmtext)
        logger.error(f'Other except error Exception', exc_info=True)
