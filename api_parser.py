import gspread
import requests
from src import config
import json
from datetime import datetime
import db.interaction
from loguru import logger

logger.add(f'log/{__name__}.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')


def do_alarm(t_alarmtext):
    headers = {"Content-type": "application/json"}
    payload = {"text": f"{t_alarmtext}", "chat_id": f"{config.admin_id}"}
    requests.post(url=config.webhook_url, data=json.dumps(payload), headers=headers)


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
        purchase_sum_element = float(key['Стоимость закупа'].replace(',', '.'))
        purchase_sum_list.append(purchase_sum_element)
    check_datetime = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    asset_sum = sum(asset_sum_list)
    purchase_sum = sum(purchase_sum_list)

    return {
        "check_datetime": check_datetime,
        "asset_sum": asset_sum,
        "purchase_sum": purchase_sum
    }


def get_actual_price():
    actual_datetime = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    btc_url = 'https://api.bitaps.com/market/v1/ticker/btcusd'
    s = requests.Session()
    btc_request = s.get(btc_url)
    btc_responce = btc_request.json()

    btc_usd = btc_responce['data']['last']

    usd_url = 'https://www.cbr-xml-daily.ru/daily_json.js'
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
    profit_rub = result['asset_actual_rub'] - result['purchase_sum']
    result['profit_rub'] = round(profit_rub, 2)

    profit_percent = result['profit_rub'] / result['purchase_sum'] * 100
    result['profit_percent'] = round(profit_percent, 2)


