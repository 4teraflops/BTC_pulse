import psutil
import time
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server
import db.interaction
from loguru import logger

logger.add(f'log/{__name__}.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')
logger.debug('test')


def get_asset_actual_sum():
    #logger.debug(f'actual_asset_sum: {db.interaction.get_actual_asset_sum()}')
    return db.interaction.get_actual_asset_sum()


def get_asset_actual_rub():
    #logger.debug(f'asset_actual_rub: {db.interaction.get_asset_actual_rub()}')
    return db.interaction.get_asset_actual_rub()


def get_profit_percent():
    #logger.debug(f'profit_percent: {db.interaction.get_profit_percent()}')
    return db.interaction.get_profit_percent()


def get_profit_rub():
    #logger.debug(f'profit_percent: {db.interaction.get_profit_percent()}')
    return db.interaction.get_profit_rub()


def get_btc_usd():
    return db.interaction.get_bts_usd()


def get_btc_rub():
    return db.interaction.get_btc_rub()


class CustomCollector(object):
    def __init__(self):
        pass

    def collect(self):
        actual_asset_sum = GaugeMetricFamily('finance_actual_asset_sum', 'количество BTC')
        actual_asset_sum_metric = get_asset_actual_sum()
        actual_asset_sum.add_metric([], actual_asset_sum_metric)

        asset_actual_rub = GaugeMetricFamily('finance_asset_actual_rub', 'Стоимость актива в рублях')
        asset_actual_rub_metric = get_asset_actual_rub()
        asset_actual_rub.add_metric([], asset_actual_rub_metric)

        profit_percent = GaugeMetricFamily('finance_profit_percent', '% профита')
        profit_percent_metric = get_profit_percent()
        profit_percent.add_metric([], profit_percent_metric)

        profit_rub = GaugeMetricFamily('finance_profit_rub', 'профит в рублях')
        profit_rub_metric = get_profit_rub()
        profit_rub.add_metric([], profit_rub_metric)

        btc_usd = GaugeMetricFamily('finance_btc_usd', 'Текущий крс битка в долларах')
        btc_usd_metric = get_btc_usd()
        btc_usd.add_metric([], btc_usd_metric)

        btc_rub = GaugeMetricFamily('finance_btc_rub', 'Текущий крс битка в рублях')
        btc_rub_metric = get_btc_rub()
        btc_rub.add_metric([], btc_rub_metric)

        yield cpu_usage
        yield ram_usage
        yield disk_usage_percent
        yield disk_free_space
        yield actual_asset_sum
        yield asset_actual_rub
        yield profit_percent
        yield profit_rub
        yield btc_usd
        yield btc_rub


def run():
    start_http_server(8001)
    REGISTRY.register(CustomCollector())
    while True:
        time.sleep(1)
