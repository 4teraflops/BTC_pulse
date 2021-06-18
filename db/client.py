import psycopg2
from src import config
from loguru import logger

logger.add(f'log/{__name__}.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')


def get_connection(db_created=False):
    """
        Могут быть проблемы, если есть другая ссессия с этой БД
    """
    if db_created:
        database = config.db_name
    else:
        database = ''

    #try:
    # Подключение к существующей базе данных
    conn = psycopg2.connect(
        user=f"{config.db_user}",
        password=f"{config.db_password}",
        host=f"{config.db_host}",
        port=f"{config.db_port}",
        database=f'{database}'
    )
    #logger.debug(f'database: {database}')
    conn.autocommit = True
    return conn
    #except (Exception, Error) as error:
    #    logger.error("Ошибка при работе с PostgreSQL", error)
    #    return "Ошибка при работе с PostgreSQL", error


def connect(rebuild_db=False):
    conn = get_connection()
    if rebuild_db:
        logger.debug('Rebuild db')
        cursor = conn.cursor()
        cursor.execute(f'DROP DATABASE IF EXISTS {config.db_name}')
        cursor.execute(f'CREATE DATABASE {config.db_name}')
        return get_connection(db_created=True)
    return get_connection(db_created=True)


def check_database(rebuild_db=False):
    logger.debug('Check db models')

    if rebuild_db:
        cursor = connect(rebuild_db=True).cursor()
    else:
        cursor = connect().cursor()

    cursor.execute("SELECT tablename FROM pg_catalog.pg_tables;")
    tables = cursor.fetchall()
    res = []

    for table in tables:
        res.append(table[0])

    #logger.debug(res)
    if 'asset' not in res:
        logger.debug('Creating table asset')
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS public.asset"
            "("
            "   id serial NOT NULL,"
            "   check_datetime timestamp without time zone NOT NULL,"
            "   asset_sum numeric NOT NULL,"
            "   purchase_sum numeric NOT NULL,"
            "   PRIMARY KEY (id)"
            ");"
            "ALTER TABLE public.asset"
            "    OWNER to postgres;"
            "COMMENT ON TABLE public.asset"
            "    IS 'Информация по номинальной стоимости актива';"
        )
    if 'actual_price' not in res:
        logger.debug('Creating table actual_price')
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS public.actual_price "
            "("
            "    id serial NOT NULL,"
            "    datetime timestamp without time zone NOT NULL,"
            "    btc_usd numeric NOT NULL,"
            "    btc_rub numeric NOT NULL,"
            "    asset_actual_rub numeric NOT NULL,"
            "    PRIMARY KEY (id)"
            ");"
            "ALTER TABLE public.actual_price "
            "    OWNER to postgres;"
            "COMMENT ON TABLE public.actual_price "
            "    IS 'Актуальные цены';"
        )
    if 'profit' not in res:
        logger.debug('Creating table profit')
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS public.profit
            (
                id serial NOT NULL,
                "timestamp" timestamp without time zone NOT NULL,
                profit_rub numeric NOT NULL,
                profit_percent numeric NOT NULL,
                PRIMARY KEY (id)
            );

            ALTER TABLE public.profit
                OWNER to postgres;

            COMMENT ON TABLE public.profit
                IS 'данные по профиту';
            '''
        )
