import db.client
import api_parser
from loguru import logger
import db.interaction
from threading import Thread
import time
import metrics.metrics

logger.add(f'log/{__name__}.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')


def main():

    # Проверка БД и таблиц
    check_db_thread = Thread(target=db.client.check_database(rebuild_db=False), daemon=True)
    check_db_thread.start()
    check_db_thread.join()
    # print("check db отработал")

    while True:

        # Обнволение данных из гугл таблицы
        update_asset_thread = Thread(target=db.interaction.update_asset)
        update_asset_thread.start()
        update_asset_thread.join()
        #print("update asset worker отработал")

        # Обновление актуальных ценников
        update_actual_price_thread = Thread(target=db.interaction.update_actual_price)
        update_actual_price_thread.start()
        update_actual_price_thread.join()
        #print("update aсtual price worker отработал")

        # Обновление расчетов профита
        update_profit_thread = Thread(target=db.interaction.update_profit)
        update_profit_thread.start()
        update_profit_thread.join()
        #print("update profit worker отработал")

        time.sleep(300)



if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        print('Stopped')
    except Exception as e:
        t_alarmtext = f'BTC_Pulse (main.py): {str(e)}'
        api_parser.do_alarm(t_alarmtext)
        logger.error(f'Other except error Exception: {e}', exc_info=True)
