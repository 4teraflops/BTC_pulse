from loguru import logger
import db.client
import api_parser

logger.add(f'log/{__name__}.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')


def update_asset():
    cursor = db.client.connect().cursor()
    payload = api_parser.get_asset()
    # logger.debug(f'payload: {payload}')
    insert_query = f'''
                        INSERT INTO asset
                        (check_datetime, asset_sum, purchase_sum) 
                        VALUES ('{payload["check_datetime"]}', '{payload["asset_sum"]}', '{payload["purchase_sum"]}');
                    '''
    cursor.execute(insert_query)
    logger.debug('Asset updated')


def get_actual_asset_sum():
    cursor = db.client.connect().cursor()
    select_query = '''
    SELECT asset_sum FROM asset
    ORDER BY id DESC
    LIMIT 1
    '''
    cursor.execute(select_query)
    result = float(cursor.fetchall()[0][0])
    # logger.debug(f'result: {type(result)}')
    return result


def update_actual_price():
    cursor = db.client.connect().cursor()
    payload = api_parser.get_actual_price()
    # logger.debug(f'payload: {payload}')
    insert_query = f'''
                        INSERT INTO actual_price
                        (datetime, btc_usd, btc_rub, asset_actual_rub)
                        VALUES ('{payload["actual_datetime"]}', '{payload["btc_usd"]}', '{payload["btc_rub"]}', '{payload["asset_actual_rub"]}');
                    '''
    cursor.execute(insert_query)
    logger.debug('actual_price updated')


def get_asset_actual_rub():
    cursor = db.client.connect().cursor()
    select_query = '''
    SELECT asset_actual_rub FROM actual_price
    ORDER BY id DESC
    LIMIT 1
    '''
    cursor.execute(select_query)
    result = float(cursor.fetchall()[0][0])
    return result


def get_purchase_sum():
    cursor = db.client.connect().cursor()
    select_query = '''
    select purchase_sum from asset
    order by id desc
    limit 1
    '''
    cursor.execute(select_query)
    result = float(cursor.fetchall()[0][0])
    return result


def update_profit():
    cursor = db.client.connect().cursor()
    payload = api_parser.calculate_profits()
    #logger.debug(f'payload: {payload}')
    insert_query = f'''
                    INSERT INTO profit
                    (timestamp, profit_rub, profit_percent)
                    VALUES ('{payload["timestamp"]}', '{payload["profit_rub"]}', '{payload["profit_percent"]}');
                    '''
    cursor.execute(insert_query)
    logger.debug('profit updated')


def get_profit_percent():
    cursor = db.client.connect().cursor()
    select_query = '''
    SELECT profit_percent FROM profit
    ORDER BY id DESC
    limit 1
    '''
    cursor.execute(select_query)
    result = float(cursor.fetchall()[0][0])
    return result


def get_profit_rub():
    cursor = db.client.connect().cursor()
    select_query = '''
    SELECT profit_rub FROM profit
    ORDER BY id DESC
    limit 1
    '''
    cursor.execute(select_query)
    result = float(cursor.fetchall()[0][0])
    return result
