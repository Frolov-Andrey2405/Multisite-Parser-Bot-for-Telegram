import mysql.connector
from .raw_query import make_query_insert_data, make_query_get_rows

def data_insert_in_db(data: dict, db_name: str, conn) -> None:
    cursor = conn.cursor()
    query = make_query_insert_data(data, db_name)
    cursor.execute(query)
    conn.commit()


def get_object(param: str, purpose_mean: str, table_name: str, conn) -> dict:
    cursor = conn.cursor()
    query = make_query_get_rows(param, purpose_mean, table_name)
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    result = tuple(cursor)
    if len(result) == 0:
        raise ValueError('В бд нет такой записи!')
    elif len(result) > 1:
        raise ValueError('Метод возвращает более одной записи!')
    
    return dict(zip(columns, result[0]))


def create_connect():
    return mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='A01082002z',
        db='allocation_parsing',
    )
