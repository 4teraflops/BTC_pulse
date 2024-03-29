import gspread
import requests
import os
import json
from datetime import datetime
import db.interaction
from loguru import logger
from dotenv import load_dotenv
import time

logger.add(f'log/{__name__}.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')


def do_alarm(t_alarmtext):
    load_dotenv()
    admin_id = os.getenv('admin_id')
    webhook_url = os.getenv('webhook_url')
    headers = {"Content-type": "application/json"}
    payload = {"text": f"{t_alarmtext}", "chat_id": f"{admin_id}"}
    requests.post(url=webhook_url, data=json.dumps(payload), headers=headers)


def get_asset():
    # Подключаемся к google sheet
    gc = gspread.service_account(filename='src/creds.json')
    sh = gc.open('Инв')
    # Выбираем вкладку
    worksheet = sh.worksheet("BTC")
    values = worksheet.get_all_records()
    #logger.info(f"values: {values}")
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


def get_actual_price():
    actual_datetime = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    btc_url = 'https://api.bitaps.com/market/v1/ticker/btcusd'
    s = requests.Session()
    attempts = 0
    while attempts < 10:
        try:
            btc_request = s.get(btc_url)
            if s.get(btc_url).status_code == 200:

                btc_response = btc_request.json()
                btc_usd = btc_response['data']['last']
                usd_url = 'https://www.cbr-xml-daily.ru/daily_json.js'
                usd_request = s.get(usd_url)
                usd_response = usd_request.json()
                usd_rub = usd_response['Valute']['USD']['Value']

                btc_rub = btc_usd * usd_rub

                asset_sum = db.interaction.get_actual_asset_sum()

                asset_actual_rub = btc_rub * asset_sum

                return {
                    "actual_datetime": actual_datetime,
                    "btc_usd": btc_usd,
                    "btc_rub": round(btc_rub, 2),
                    "asset_actual_rub": round(asset_actual_rub, 2)
                }

        except requests.exceptions.ConnectionError:
            logger.error('Connection Error. Get pause 60s and trying again...')
            attempts += 1
            time.sleep(6)




def calculate_profits():
    asset_actual_rub = db.interaction.get_asset_actual_rub()
    purchase_sum = db.interaction.get_purchase_sum()
    profit_rub = round(asset_actual_rub - purchase_sum, 2)
    timestamp = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    try:
        profit_percent = round(profit_rub / purchase_sum * 100, 2)
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
