import gspread
import requests
from src import config
import json
from datetime import datetime
import db.interaction
from loguru import logger
import time

logger.add(f'log/{__name__}.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')


def do_alarm(t_alarmtext):
    headers = {"Content-type": "application/json"}
    payload = {"text": f"{t_alarmtext}", "chat_id": f"{config.admin_id}"}
    requests.post(url=config.webhook_url, data=json.dumps(payload), headers=headers)


@logger.catch()
def get_asset():
    # Подключаемся к google sheet
    gc = gspread.service_account(filename='src/creds.json')
    sh = gc.open('Инв')
    # Выбираем вкладку
    worksheet = sh.worksheet("BTC")
    values = worksheet.get_all_records()
    asset_sum_list = []
    purchase_sum_list = []
    for key in values:
        asset_sum_element = float(key['Кол-во'].replace(',', '.'))
        asset_sum_list.append(asset_sum_element)

        try:
            purchase_sum_element = float(key['Стоимость закупа'].replace(',', '.'))
        except AttributeError:
            purchase_sum_element = float(key['Стоимость закупа'])

        purchase_sum_list.append(purchase_sum_element)
    check_datetime = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    asset_sum = sum(asset_sum_list)
    purchase_sum = sum(purchase_sum_list)

    return {
        "check_datetime": check_datetime,
        "asset_sum": asset_sum,
        "purchase_sum": purchase_sum
    }


@logger.catch()
def get_actual_price():
    actual_datetime = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    btc_url = 'https://api.bitaps.com/market/v1/ticker/btcusd'
    s = requests.Session()
    btc_request = s.get(btc_url)
    btc_responce = btc_request.json()

    btc_usd = btc_responce['data']['last']

    usd_url = 'https://www.cbr-xml-daily.ru/daily_json.js'
    try:
        usd_request = s.get(usd_url)
    except requests.exceptions.ConnectionError():  # Если ошибка подключения, то взять тймаут на 10с и повторно
        logger.warning('https://www.cbr-xml-daily.ru/daily_json.js не отвечает. Таймаут 10с.')
        time.sleep(10)
        usd_request = s.get(usd_url)
    usd_responce = usd_request.json()
    usd_rub = usd_responce['Valute']['USD']['Value']

    btc_rub = btc_usd * usd_rub

    asset_sum = db.interaction.get_actual_asset_sum()
    #logger.debug(f'asset_sum: {asset_sum}')
    #result['btc_rub'] = round(btc_rub, 2)
    asset_actual_rub = btc_rub * asset_sum

    return {
        "actual_datetime": actual_datetime,
        "btc_usd": btc_usd,
        "btc_rub": round(btc_rub, 2),
        "asset_actual_rub": round(asset_actual_rub, 2)
    }


def calculate_profits():
    asset_actual_rub = db.interaction.get_asset_actual_rub()
    purchase_sum = db.interaction.get_purchase_sum()
    profit_rub = round(asset_actual_rub - purchase_sum, 2)
    timestamp = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    try:
        profit_percent = round(profit_rub / purchase_sum * 100, 2)
        #logger.debug(f"profit_percent=")
        #logger.debug(f'asset_actual_rub: {asset_actual_rub}\npurchase_sum: {purchase_sum}\nprofit_rub: {profit_rub}\nprofit_percent: {profit_percent}')
        return {
            "timestamp": timestamp,
            "profit_rub": profit_rub,
            "profit_percent": profit_percent
        }
    except ZeroDivisionError:
        return {
            "timestamp": timestamp,
            "profit_rub": profit_rub,
            "profit_percent": '0'
            }


