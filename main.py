import gspread
import requests
import config
import json
from datetime import datetime, timedelta
import time


result = {'asset_datetime': '2021-06-17 00:22:57'}


def do_alarm(t_alarmtext):
    headers = {"Content-type": "application/json"}
    payload = {"text": f"{t_alarmtext}", "chat_id": f"{config.admin_id}"}
    requests.post(url=config.webhook_url, data=json.dumps(payload), headers=headers)


def get_asset():
    # Обновлять 1 раз в сутки
    asset_datetime = datetime.strptime(result['asset_datetime'], "%Y-%m-%d %H:%M:%S")
    delay = (datetime.now() - asset_datetime).seconds
    print(f'\ndelay: {delay}\n')

    if delay > 100:
        # Подключаемся к google sheet
        gc = gspread.service_account(filename='creds.json')
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
        asset_sum = sum(asset_sum_list)
        purchase_sum = sum(purchase_sum_list)
        result['asset_sum'] = asset_sum
        result['purchase_sum'] = round(purchase_sum, 2)

        result['asset_datetime'] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")

    else:
        pass


def get_actual_price():
    btc_url = 'https://api.bitaps.com/market/v1/ticker/btcusd'
    s = requests.Session()
    btc_request = s.get(btc_url)
    btc_responce = btc_request.json()

    btc_usd = btc_responce['data']['last']
    result['btc_usd'] = btc_usd

    usd_url = 'https://www.cbr-xml-daily.ru/daily_json.js'
    usd_request = s.get(usd_url)
    usd_responce = usd_request.json()
    usd_rub = usd_responce['Valute']['USD']['Value']

    btc_rub = result['btc_usd'] * usd_rub
    result['btc_rub'] = round(btc_rub, 2)

    result['asset_actual_rub'] = round(result['btc_rub'] * result['asset_sum'], 2)


def calculate_profits():
    profit_rub = result['asset_actual_rub'] - result['purchase_sum']
    result['profit_rub'] = round(profit_rub, 2)

    profit_percent = result['profit_rub'] / result['purchase_sum'] * 100
    result['profit_percent'] = round(profit_percent, 2)


if __name__ == '__main__':
    while True:
        try:
            get_asset()
            get_actual_price()
            calculate_profits()
            for key in result:
                print(key, result[key])
            time.sleep(10)
        except KeyboardInterrupt:
            print('Stopped')
    #    except Exception as e:
    #        t_alarmtext = f'BTC_Pulse (main.py): {str(e)}'
    #        do_alarm(t_alarmtext)
    #        logger.error(f'Other except error Exception', exc_info=True)
