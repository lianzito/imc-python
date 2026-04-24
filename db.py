import mysql.connector
from mysql.connector import Error, pooling

DB_PARAMS = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'imc_python',
    'charset': 'utf8mb4',
    'time_zone': '-03:00',
    'use_pure': True,
    'connect_timeout': 10, 
}

_pool = pooling.MySQLConnectionPool(
    pool_name='imc_pool',
    pool_size= 5,
    **DB_PARAMS
)

def get_connection():
    try:
        return _pool.get_connection()
    except Error as e:
        raise Exception(f'Erro ao obeter conexão no pool: {e}')
    
def execute_query(sql, params=None, fetch=False):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())

        if fetch:
            return cursor.fetchall()
        else:
            conn.commit()
            return cursor.rowcount

    except Error as e:
        conn.rollback()
        raise Exception(f'Erro ao executar querry: {e}')
    finally:
        cursor.close()
        conn.close()    

def execute_one(sql, params=None):
    resultados = execute_query(sql, params, fetch=True)
    return resultados[0] if resultados else None
