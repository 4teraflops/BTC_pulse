import db.client
import api_parser
from loguru import logger
from datetime import datetime, timedelta
import db.interaction
from threading import Thread
import time
import metrics.metrics

logger.add(f'log/{__name__}.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')


class UpdateActualPrice(Thread):
    # Актуальные цены апдейтим каждые 3 минуты
    def run(self):
        while True:
            db.interaction.update_actual_price()
            time.sleep(180)


class UpdateAsset(Thread):
    # Инфу по активу апдейтим каждые 12 часов
    def run(self):
        while True:
            db.interaction.update_asset()
            time.sleep(43200)


class UpdateProfit(Thread):
    # Профит апдейтим каждые 3 минуты
    def run(self):
        while True:
            db.interaction.update_profit()
            time.sleep(180)


if __name__ == '__main__':
    try:
        # Проверка БД и таблиц
        check_db_thread = Thread(target=db.client.check_database(rebuild_db=False), daemon=True)
        #now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        # Обнволение данных из гугл таблицы
        #update_asset_thread = Thread(target=db.interaction.update_asset(), daemon=True)
        # Обновление актуальных ценников
        #update_actual_price = Thread(target=api_parser.get_actual_price(), daemon=True)

        check_db_thread.start()

        UpdateActualPrice_worker = UpdateActualPrice()
        UpdateActualPrice_worker.start()

        UpdateProfit_worker = UpdateProfit()
        UpdateProfit_worker.start()

        UpdateAsset_worker = UpdateAsset()
        UpdateAsset_worker.start()

        Metrics_worker = metrics.metrics.run()
        Metrics_worker.start()

    except KeyboardInterrupt:
        print('Stopped')
    #except Exception as e:
    #    t_alarmtext = f'BTC_Pulse (parser.py): {str(e)}'
    #    api_parser.do_alarm(t_alarmtext)
    #    logger.error(f'Other except error Exception: {e}', exc_info=True)
